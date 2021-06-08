import { AfterViewChecked, Component, ViewChild, Renderer2, ElementRef } from '@angular/core';
import {environment} from '../../environments/environment';
import {grpc} from "@improbable-eng/grpc-web";
import {Shengji} from "proto-gen/shengji_pb_service";
import {CreateGameRequest, EnterRoomRequest, AddAIPlayerRequest, PlayHandRequest, Game as GameProto, Hand as HandProto, Card as CardProto, Player as PlayerProto} from "proto-gen/shengji_pb";
import { AlertController } from '@ionic/angular';
import { ActivatedRoute, Router } from '@angular/router';
declare var cards:any;

@Component({
  selector: 'app-game',
  templateUrl: './game.page.html',
  styleUrls: ['./game.page.scss'],
})

export class GamePage implements AfterViewChecked {
@ViewChild('cardTable') tableElement: ElementRef;
@ViewChild('gameInfo', { static: false }) gameInfo: ElementRef;
  nativeElement: any;
  gameId = 'None';
  started = false;
  createGame = true;
  game: Game = null;
  playerId = "None";

  constructor(private route: ActivatedRoute, private router: Router, public alertController: AlertController, private renderer:Renderer2) {
    if (this.router.getCurrentNavigation().extras.state) {
      this.createGame = this.router.getCurrentNavigation().extras.state.createGame;
    }
    console.log("game page, createGame is "+this.createGame);
    if (this.createGame) {
      this.roomCreationPrompt();
    } else {
      this.roomJoinPrompt();
    }
  }

  // TODO(Aaron): Check if this can be replaced by ionViewDidEnter
  ngAfterViewChecked() {
    if (!this.started) {
      if (this.tableElement.nativeElement.offsetHeight === 0) {
        return;
      }
      this.started = true;
      this.nativeElement = this.tableElement.nativeElement;
    }
  }

  async roomCreationPrompt() {
    const alert = await this.alertController.create({
      // TODO(Aaron): Add better css to the prompt like cssClass: 'my-custom-class',
      header: 'Please Enter Your Name:',
      inputs: [
        {
          name: 'player_name',
          id: 'player_name',
          type: 'text',
          placeholder: '<My Name>'
        },
      ],
      buttons: [
        {
          text: 'Cancel',
          role: 'cancel',
          cssClass: 'secondary',
          handler: () => {
            console.log('Player refuses to enter name.');
            this.router.navigate(['/']);
          }
        }, {
          text: 'Ok',
          handler: (inputData) => {
            console.log('Player entered: '+JSON.stringify(inputData));
            this.playerId = inputData.player_name;
            this.startGame(inputData.player_name);
          }
        }
      ]
    });
    await alert.present();
  }
  async roomJoinPrompt() {
    const alert = await this.alertController.create({
      // TODO(Aaron): Add better css to the prompt like cssClass: 'my-custom-class',
      header: 'Please Enter Game Room ID and Your Name:',
      inputs: [
        {
          name: 'game_id',
          id: 'game_id',
          type: 'text',
          placeholder: '<Game Room ID>'
        },
        {
          name: 'player_name',
          id: 'player_name',
          type: 'text',
          placeholder: '<My Name>'
        },
      ],
      buttons: [
        {
          text: 'Cancel',
          role: 'cancel',
          cssClass: 'secondary',
          handler: () => {
            console.log('Player refuses to enter game ID or name.');
            this.router.navigate(['/']);
          }
        }, {
          text: 'Ok',
          handler: (inputData) => {
            console.log('Player entered: '+JSON.stringify(inputData));
            this.gameId = inputData.game_id;
            this.playerId = inputData.player_name;
            this.enterRoom(inputData.player_name, inputData.game_id);
          }
        }
      ]
    });
    await alert.present();
  }
  addAIPlayer() {
    const createAIRequest = new AddAIPlayerRequest();
    createAIRequest.setGameId(this.gameId);
    console.log('Adding AI Player for: '+this.gameId);
    const playHandReq = new PlayHandRequest();
    grpc.unary(Shengji.addAIPlayer, {
      request: createAIRequest,
      host: environment.grpcUrl,
      onEnd: res => {
        const { status, statusMessage, headers, message, trailers } = res;
        if (status === grpc.Code.OK && message) {
          var AIName = message.toObject()['playerName']
          console.log(AIName + " is added to room");
        }
      }
    });
  }
  startGame(player_name: string) {
    const createGameRequest = new CreateGameRequest();
    createGameRequest.setPlayerId(player_name);
    grpc.unary(Shengji.createGame, {
      request: createGameRequest,
      host: environment.grpcUrl,
      onEnd: res => {
        const { status, statusMessage, headers, message, trailers } = res;
        if (status === grpc.Code.OK && message) {
          this.gameId = message.toObject()['gameId']
          const gameIdText = this.renderer.createText('Room ID: '+this.gameId);
          this.renderer.appendChild(this.gameInfo.nativeElement, gameIdText);

          console.log("Created game object: ", message.toObject());
          this.enterRoom(player_name, this.gameId);
        }
      }
    });
  }
  enterRoom(player_name: string, game_id: any) {
    const enterRoomRequest = new EnterRoomRequest();
    enterRoomRequest.setPlayerId(player_name);
    enterRoomRequest.setGameId(game_id);
    grpc.invoke(Shengji.enterRoom, {
      request: enterRoomRequest,
      host: environment.grpcUrl,
      onMessage: (message: GameProto) => {
        console.log("Current game state: ", message.toObject());
        if (this.game == null ) {
          this.game = new Game(this.nativeElement.clientHeight, this.nativeElement.clientWidth, this.playerId, this.gameId);
        }
        switch (message.getUpdateCase()) {
          case GameProto.UpdateCase.NEW_PLAYER_UPDATE:
              this.game.addPlayer(message.getNewPlayerUpdate().getPlayerId());
              if (this.game.players.length == 4) {
                this.game.start();
              }
            break;
          case GameProto.UpdateCase.CARD_DEALT_UPDATE:
            let cardDealtUpdate = message.getCardDealtUpdate();
            this.game.renderCardDealt(cardDealtUpdate.getPlayerId(), cardDealtUpdate.getCard())
            break;
          case GameProto.UpdateCase.KITTY_HIDDEN_UPDATE:
            let kittyHiddenUpdate = message.getKittyHiddenUpdate();
            this.game.renderKittyHiddenUpdate(kittyHiddenUpdate.getKittyPlayerId(), message.getKitty().getCardsList().map(c => Card.fromProto(c)));
            break;
          default:
            console.log("Invalid update");
            break;
        }
      },
      onEnd: (code: grpc.Code, msg: string | undefined, trailers: grpc.Metadata) => {
        if (code == grpc.Code.OK) {
          console.log("all ok")
        } else {
          console.log("hit an error", code, msg, trailers);
        }
      }
    });
  }
}

export enum Suit {
  None,
  Spades,
  Hearts,
  Clubs,
  Diamonds,
  Joker,
  Trump
}

enum GameStage {
  Deal,
  DealKitty,
  HideKitty,
  Play,
  Busy
}

enum DeclaredTrump {
  None,
  Single,
  Pair,
  Jokers
}

// Global utilities.
// Convert a Card protobuf definition to cardUI definition in cards.js
const getCardUISuitFromProto = function(cardProto: CardProto) : any {
  switch(cardProto.getSuit()) {
    case CardProto.Suit.SMALL_JOKER: return 'bj';
    case CardProto.Suit.BIG_JOKER: return 'rj';
    case CardProto.Suit.HEARTS: return 'h';
    case CardProto.Suit.SPADES: return 's';
    case CardProto.Suit.CLUBS: return 'c';
    case CardProto.Suit.DIAMONDS: return 'd';
    default: throw Error("Cannot process proto: " + cardProto);
  }
}

const getCardProtoSuit = function(cardUI: any) : any {
  switch(cardUI.suit) {
    case "rj": return CardProto.Suit.BIG_JOKER;
    case "bj": return CardProto.Suit.SMALL_JOKER;
    case "s": return CardProto.Suit.SPADES;
    case "h": return CardProto.Suit.HEARTS;
    case "c": return CardProto.Suit.CLUBS;
    case "d": return CardProto.Suit.DIAMONDS;
    default: throw Error("Cannot process card ui: " + cardUI);
  }
}

const toCardProto = function(cardUI: any) : CardProto {
  const cardProto = new CardProto();
  cardProto.setSuit(getCardProtoSuit(cardUI));
  cardProto.setRank(cardUI.rank);
  return cardProto;
}

// create a Card representation of the UI representation from javascript
const toCard = function(cardUI: any) : Card {
  switch(cardUI.suit) {
    case "bj": return Card.smallJoker;
    case "rj": return Card.bigJoker;
    case "s": return new Card(Suit.Spades, cardUI.rank);
    case "h": return new Card(Suit.Hearts, cardUI.rank);
    case "c": return new Card(Suit.Clubs, cardUI.rank);
    case "d": return new Card(Suit.Diamonds, cardUI.rank);
    default: throw Error("Cannot process card ui: " + cardUI);
  }
}

const cardsEquals = function(card: Card, otherCard: Card) : boolean {
  return card.suit === otherCard.suit && card.rank === otherCard.rank;
}

// cards and cardUIs must be in order.
const resolveCardUIs = function(cards: Card[], cardUIs: any[]) : any[] {
  let resolvedCardUIs: any[] = [];
  let i = 0;
  let j = 0;

  while (i < cards.length) {
    let found = false;
    while (j < cardUIs.length) {
      let cardUI = cardUIs[j++];
      if (cardsEquals(cards[i], toCard(cardUI))) {
        found = true;
        resolvedCardUIs.push(cardUI);
        break;
      }
    }
    if (!found) {
      throw Error("Could not resolve " + cards[i] + " from players hand");
    }
    i++;
  }

  return resolvedCardUIs;
}

// Card abstraction, mock type used for gRPC
export class Card {
  suit: Suit;
  rank: number;

  constructor(suit: Suit, rank: number) {
    this.suit = suit;
    this.rank = rank;
  }

  static none: Card = new Card(Suit.None, 0);
  static smallJoker: Card = new Card(Suit.Joker, 1);
  static bigJoker: Card = new Card(Suit.Joker, 2);

  static fromProto(cardProto: CardProto): Card {
    let suit: Suit = null;
    let rank: number = 0;

    switch (cardProto.getSuit()) {
      case CardProto.Suit.SUIT_UNDEFINED:
        return this.none;
      case CardProto.Suit.BIG_JOKER:
        return this.bigJoker;
      case CardProto.Suit.SMALL_JOKER:
        return this.smallJoker;
      case CardProto.Suit.SPADES:
        suit = Suit.Spades;
        break;
      case CardProto.Suit.HEARTS:
        suit = Suit.Hearts;
        break;
      case CardProto.Suit.CLUBS:
        suit = Suit.Clubs;
        break;
      case CardProto.Suit.DIAMONDS:
        suit = Suit.Diamonds;
        break;
    }

    // cardProto.getRank() returns an enum Card.Rank but we use it as a number
    return new Card(suit, cardProto.getRank());
  }

  public toString(): string {
    return Suit[this.suit] + this.rank;
  }
}

export class CardRanking {
  trumpSuit = Suit.None;
  trumpRank: number;
  uiRanks = new Map();
  functionalRanks = new Map();

  constructor(rank: number) {
    this.trumpRank = rank;
    this.resetOrder(this.trumpSuit);
  }

  resetOrder(suit: Suit) {
    this.trumpSuit = suit;
    const nonTrumpSuits = [Suit.Spades, Suit.Hearts, Suit.Clubs, Suit.Diamonds].filter((s) => s !== this.trumpSuit);
    let uiRank = 0;
    let functionalRank = 0;
    let that = this;
    let setRank = function(card: Card, incrementFunctionalRank: boolean = true) {
      that.uiRanks.set(card.toString(), uiRank++);
      that.functionalRanks.set(card.toString(), functionalRank);
      if (incrementFunctionalRank) functionalRank++;
    }

    // Jokers
    setRank(Card.bigJoker);
    setRank(Card.smallJoker);

    // Trump suit + Trump rank
    if (this.trumpSuit !== Suit.None && this.trumpSuit !== Suit.Joker) {
      setRank(new Card(this.trumpSuit, this.trumpRank));
    }

    // Trump rank
    for (const suit of nonTrumpSuits) {
      setRank(new Card(suit, this.trumpRank), false);
    }
    functionalRank++;

    // Trump suit
    if (this.trumpSuit !== Suit.None && this.trumpSuit !== Suit.Joker) {
      setRank(new Card(this.trumpSuit, 1));
      for (let rank = 13; rank > 1; rank--) {
        if (rank !== this.trumpRank) {
          setRank(new Card(this.trumpSuit, rank));
        }
      }
    }

    // Others
    for (const suit of nonTrumpSuits) {
      setRank(new Card(suit, 1));
      for (let rank = 13; rank > 1; rank--) {
        if (rank !== this.trumpRank) {
          setRank(new Card(suit, rank));
        }
      }
    }
  }

  // For display order and sorting
  getUIRank(card: Card) : number {
    return this.uiRanks.get(card.toString());
  }

  // For tractor and trick resolution
  getFunctionRank(card: Card) : number {
    return this.functionalRanks.get(card.toString());
  }

  // For determing winning tricks
  getFunctionalSuit(card: Card) : Suit {
    if (card.suit === Suit.Joker || card.rank === this.trumpRank || card.suit === this.trumpSuit) {
      return Suit.Trump;
    }
    return card.suit;
  }
}

class Tractor {
  highCard: Card;
  length: number;

  constructor(card: Card, length: number) {
    this.highCard = card;
    this.length = length;
  }

  public toString(): string {
    return this.highCard + ":" + length;
  }
}

// Unnecessary if there is GroupBy
class TractorGroup {
  length: number;
  tractors: Tractor[] = [];

  constructor(length: number) {
    this.length = length;
  }
}

class TrickFormat {
  suit: Suit;
  length: number;
  tractorGroups: TractorGroup[] = [];
  pairs: Card[] = [];
  singles: Card[] = [];

  static invalid = new TrickFormat(Suit.None, 0);

  constructor(suit: Suit, length: number) {
    this.suit = suit;
    this.length = length;
  }

  // TODO: Greedy isn't completely accurate, DP is likely necessary
  // For example, tractors [3, 2, 2] is satisfied by [4, 3] but not vice versa
  // Currently, exact format is required
  isSatisfiedBy(format: TrickFormat) : boolean {
    if (this.tractorGroups.length !== format.tractorGroups.length) {
      console.log("Number of tractor groups do not match");
      return false;
    }

    this.tractorGroups.sort((a, b) => b.length - a.length);
    format.tractorGroups.sort((a, b) => b.length - a.length);

    for (let i = 0; i < this.tractorGroups.length; i++) {
      if (this.tractorGroups[i].length !== format.tractorGroups[i].length) {
        console.log("Tractor group lengths do not match");
        return false;
      }
      if (this.tractorGroups[i].tractors.length !== format.tractorGroups[i].tractors.length) {
        console.log("Tractor lengths do not match");
        return false;
      }
    }

    if (this.pairs.length !== format.pairs.length) {
      console.log("Number of pairs do not match");
      return false;
    }

    if (this.singles.length !== format.singles.length) {
      console.log("Number of pairs do not match");
      return false;
    }

    return true;
  }

  public toString(): string {
    if (this.length === 0) {
      return "Invalid format";
    }
    if (this.suit === Suit.None) {
      return "Mixed format";
    }
    let format = "Suit: " + this.suit;
    format += "\nTractor: ";
    for (const tractorGroup of this.tractorGroups) {
      for (const tractor of tractorGroup.tractors) {
        format += tractor + ", ";
      }
    }
    format += "\nPairs: " + this.pairs.length;
    format += "\nSingles: " + this.singles.length;
    return format;
  }
}

class TrickPile {
  game: Game;
  players: Player[];
  ranking: CardRanking;
  cardsPlayedUI: any[];
  trickFormat: TrickFormat | null = null;
  winningPlayer: number | null = null;
  winningHand: TrickFormat | null = null;

  constructor(game: Game, players: Player[], ranking: CardRanking, x: number, y: number) {
    this.game = game;
    this.players = players;
    this.ranking = ranking;
    this.cardsPlayedUI = [players.length];
    for (let i = 0; i < players.length; i++) {
      let vector = [players[i].x - x, players[i].y - y];
      let magnitude = Math.sqrt(vector[0]*vector[0] + vector[1]*vector[1]);
      this.cardsPlayedUI[i] = new cards.Hand({faceUp: true,
        x:x + vector[0]*this.game.cardWidth()/magnitude,
        y:y + vector[1]*this.game.cardHeight()/magnitude
      })
    }
  }

  initialize(ranking: CardRanking) {
    this.ranking = ranking;
  }

  // Currently assumes cards are of the same suit, consider moving mixed suit logic here
  resolveFormat(cards: Card[]): TrickFormat {
    let format = new TrickFormat(this.ranking.getFunctionalSuit(cards[0]), cards.length);

    // Resolve singles and pairs
    let i = 0;
    while (i < cards.length) {
      if (i < cards.length - 1 && cardsEquals(cards[i], cards[i+1])) {
        format.pairs.push(cards[i]);
        i += 2;
      }
      else {
        format.singles.push(cards[i]);
        i++;
      }
    }

    // Resolve tractors
    i = 0;
    while (i < format.pairs.length) {
      let j = i;
      // Find longest run
      while (j < format.pairs.length - 1
        && this.ranking.getUIRank(format.pairs[j+1]) - this.ranking.getUIRank(format.pairs[j]) === 1) {
        j++;
      }
      if (i !== j) {
        let length = j - i + 1;
        let tractorGroup = format.tractorGroups.find(tractorGroup => tractorGroup.length === length);

        if (!tractorGroup) {
          tractorGroup = new TractorGroup(length);
          format.tractorGroups.push(tractorGroup);
        }

        tractorGroup.tractors.push(new Tractor(format.pairs[i], j - i + 1));
        format.pairs.splice(i, j - i + 1);
      }
      else {
        i++;
      }
    }

    return format;
  }

  // If play is not legal, return invalid format
  // Otherwise return the resolved format
  // Non-lead, non-trump suits are returned as mixed format with Suit.None
  resolveLegalFormat(playerIndex: number, cards: Card[]): TrickFormat {
    // Check legality of lead
    if (this.trickFormat === null) {
      // Currently can only resolve leading plays with one suit
      let suit = this.ranking.getFunctionalSuit(cards[0]);
      for (const card of cards) {
        if (suit !== this.ranking.getFunctionalSuit(card)) {
          console.log("Cards cannot be played since more than one suit detected");
          return TrickFormat.invalid;
        }
      }

      let format = this.resolveFormat(cards);
      if (format.tractorGroups.length + format.pairs.length + format.singles.length > 1) {
        // TODO: Check legality of throw, need to return a status indicating punishment
      }

      this.trickFormat = format;
      return this.trickFormat;
    }

    if (cards.length !== this.trickFormat.length) {
      console.log("Length of cards played does not match lead.")
      return TrickFormat.invalid;
    }

    // Follow suit if possible
    let suitCardsInHand = this.players[playerIndex].handUI.map(ui => toCard(ui))
      .filter(c => this.ranking.getFunctionalSuit(c) === this.trickFormat.suit);
    let suitTotalInHand = suitCardsInHand.length;
    let suitTotalInPlay = cards.filter(card =>
      this.ranking.getFunctionalSuit(card) === this.trickFormat.suit).length;

    if (suitTotalInPlay < Math.min(suitTotalInHand, this.trickFormat.length)) {
      console.log("Not all playable cards of the lead suit were played.");
      return TrickFormat.invalid;
    }

    if (suitTotalInHand >= this.trickFormat.length) {
      console.log("Full follow");
      // All cards played must be of the leading suit
      let format = this.resolveFormat(cards);

      if (format === TrickFormat.invalid || format.suit === Suit.None) {
        throw Error("Invalid format or mixed hand. This should not occur.");
      }

      let handFormat = this.resolveFormat(suitCardsInHand);

      let trickTractors = this.trickFormat.tractorGroups.map(g => g.tractors).reduce((a, b) => a.concat(b), []);
      let handTractors = handFormat.tractorGroups.map(g => g.tractors).reduce((a, b) => a.concat(b), []);
      let playedTractors = format.tractorGroups.map(g => g.tractors).reduce((a, b) => a.concat(b), []);
      let unsatisfiedTractors: Tractor[] = [];

      for (const tractor of trickTractors) {
        // TODO: handle tractor subsets (i.e. length of 3 satisfies length of 2)
        let satisfiableTractor = handTractors.filter(t => t.length === tractor.length);
        if (satisfiableTractor.length > 0) {
          let handTractor: Tractor = undefined
          let playedTractor = playedTractors.find(pt => satisfiableTractor.find(st => {
            let compareResult = cardsEquals(pt.highCard, st.highCard) && pt.length === st.length;
            if (compareResult) {
              handTractor = st;
            }
            return compareResult;
          }) !== undefined);

          if (playedTractor === undefined) {
            console.log("Not all playable tractors of the lead suit were played.");
            return TrickFormat.invalid;
          }

          //Remove satisfied tractors
          handTractors.splice(handTractors.indexOf(handTractor), 1);
          playedTractors.splice(playedTractors.indexOf(playedTractor), 1);
        }
        else {
          unsatisfiedTractors.push(tractor);
        }
      }

      let pairsInPlayedTractors = playedTractors.map(t => t.length).reduce((a, b) => a + b, 0);
      let pairsInUnsatisfiedTractors = unsatisfiedTractors.map(t => t.length).reduce((a, b) => a + b, 0);
      let pairsInHandTractors = handTractors.map(t => t.length).reduce((a, b) => a + b, 0);

      if (format.pairs.length + pairsInPlayedTractors
        < Math.min(this.trickFormat.pairs.length + pairsInUnsatisfiedTractors, handFormat.pairs.length + pairsInHandTractors)) {
        console.log("Not all playable pairs of the lead suit were played.");
        console.log("Number of pairs played: " + format.pairs.length);
        console.log("Number of pairs in hand: " + handFormat.pairs.length);
        console.log("Number of pairs in tractors in hand: " + pairsInHandTractors);
        return TrickFormat.invalid;
      }

      if (this.trickFormat.isSatisfiedBy(format)) {
        console.log("Matching format, valid");
        return format;
      }
      else {
        console.log("Mixed format, valid");
        return new TrickFormat(Suit.None, format.length);
      }
    }

    if (suitTotalInHand > 0 && suitTotalInHand < this.trickFormat.length) {
      // Must be a mixed format
      console.log("Partial follow, valid");
      return new TrickFormat(Suit.None, cards.length);
    }

    if (suitTotalInHand === 0) {
      // Check for a mixed format
      for (const card of cards) {
        if (this.ranking.getFunctionalSuit(card) !== Suit.Trump) {
          console.log("Can't follow, mixed format, valid");
          return new TrickFormat(Suit.None, cards.length);
        }
      }

      // Must be an all trump format
      let format = this.resolveFormat(cards);
      if (format.suit != Suit.Trump) {
        throw new Error("We shoud never resolve the format when non-trumps follow a leading suit");
      }

      if (this.trickFormat.isSatisfiedBy(format)) {
        console.log("Can't follow, trump format, valid");
        return format;
      }
      else {
        console.log("Can't follow, mixed trump format, valid");
        return new TrickFormat(Suit.None, cards.length);
      }
    }

    console.log("Unknown format, invalid");
    return TrickFormat.invalid;
  }

  play(playerIndex: number, cards: Card[]): boolean {
    let resolvedFormat = this.resolveLegalFormat(playerIndex, cards);
    console.log(resolvedFormat);

    if (resolvedFormat === TrickFormat.invalid) {
      return false;
    }

    this.cardsPlayedUI[playerIndex].addCards(resolveCardUIs(cards, this.players[playerIndex].handUI));
    this.cardsPlayedUI[playerIndex].render();
    this.players[playerIndex].handUI.render();

    if (resolvedFormat.suit !== Suit.None) {
      // Leading play
      if (this.winningHand === null) {
        this.winningHand = resolvedFormat;
        this.winningPlayer = playerIndex;
      }
      // Following play
      else {
        let that = this;
        let champDefends = function(champCards: Card[], challengerCards: Card[]) : boolean {
          champCards.sort((a, b) => that.ranking.getFunctionRank(a) - that.ranking.getFunctionRank(b));
          challengerCards.sort((a, b) => that.ranking.getFunctionRank(a) - that.ranking.getFunctionRank(b));
          for (let i = 0; i < champCards.length; i++) {
            if (that.ranking.getFunctionRank(challengerCards[i]) >= that.ranking.getFunctionRank(champCards[i])) {
              return true;
            }
          }
          return false;
        }

        // TODO: this trick winning logic is too strict according to wiki, though in my experience it's different.
        for (let i = 0; i < this.winningHand.tractorGroups.length; i++) {
          let winningTractors = this.winningHand.tractorGroups[i].tractors.map(t => t.highCard);
          let challengerTractors = resolvedFormat.tractorGroups[i].tractors.map(t => t.highCard);

          if (champDefends(winningTractors, challengerTractors)) {
            // Challenger did not win
            console.log("Challenger lost on tractor");
            return true;
          }
        }

        if (champDefends(this.winningHand.pairs, resolvedFormat.pairs)) {
          console.log("Challenger lost on pair");
          return true;
        }

        if (champDefends(this.winningHand.singles, resolvedFormat.singles)) {
          console.log("Challenger lost on single");
          return true;
        }

        // Challenger won
        console.log("Challenger won");
        this.winningHand = resolvedFormat;
        this.winningPlayer = playerIndex;
      }
    }

    return true;
  }

  async getWinner() : Promise<number | null> {
    if (this.cardsPlayedUI.some(p => p.length === 0)) {
      return null;
    }

    // Pause so players can see all cards
    await new Promise(r => setTimeout(r, 2000));

    let winnerUI = this.players[this.winningPlayer].tricksWonUI;
    let cards = [];
    for (let play of this.cardsPlayedUI) {
      for (let i = 0; i < play.length; i++) {
        cards.push(play[i]);
      }
    }
    winnerUI.addCards(cards);
    winnerUI.render();

    let winner = this.winningPlayer;

    this.trickFormat = null;
    this.winningHand = null;
    this.winningPlayer = null;

    return winner;
  }
}

class Player {
  game: Game;
  name: string;
  index: number;
  x: number;
  y: number;
  handUI;
  tricksWonUI;
  selectedCardUIs = new Set<any>();
  // Used by Angular in HTML template.
  label_left: string;
  label_top: string;

  constructor(game: Game, index: number, name: string, x: number, y: number) {
    this.game = game;
    this.index = index;
    this.name = name;
    this.x = x;
    this.y = y;
    this.handUI = new cards.Hand({faceUp: true, x:x, y:y - (game.cardHeight() + game.cardMargin) / 2});
    this.tricksWonUI = new cards.Hand({faceUp: true, x:x, y:y + (game.cardHeight() + game.cardMargin) / 2});
    let that = this;
    this.handUI.click((c, e) => that.act(c, e));
    // TODO: The proper way to center this would be to find the text width in
    // px of the DOM element and divide by half, 5 is good enough for now for
    // ASCII characters, I guess...
    this.label_left = (x-this.name.length*5) + "px";
    this.label_top = y + "px";
  }

  render(options?: any) {
    this.handUI.sort((a, b) => this.game.cardRanking.getUIRank(toCard(a)) - this.game.cardRanking.getUIRank(toCard(b)));
    this.handUI.render(options);
  }

  act(cardUI: any, event: any) {
    // prevent context menu on right click
    event.preventDefault();

    // select or deselect with click
    if (event.type === "click") {
      if (this.selectedCardUIs.has(cardUI)) {
        this.selectedCardUIs.delete(cardUI);
        cardUI.yAdjustment = 0;
        this.handUI.render();
        return;
      }

      cardUI.yAdjustment = -this.game.cardHeight()*4/10;
      this.selectedCardUIs.add(cardUI);

      this.handUI.render();
    }
    // submit play with right click
    else if (event.type === "contextmenu") {
      // Ignore if right clicked an unselected card
      if (!this.selectedCardUIs.has(cardUI)) return;

      // Set all proto field for the PlayHandRequest.
      const playHandReq = new PlayHandRequest();
      playHandReq.setPlayerId(this.game.playerId);
      playHandReq.setGameId(this.game.gameId);
      // TODO: Set the real intention somehow...
      playHandReq.setIntention(PlayHandRequest.Intention.HIDE_KITTY);

      const handToPlay = new HandProto();
      let cardsProto = Array.from(this.selectedCardUIs.values()).map(ui => toCardProto(ui));
      handToPlay.setCardsList(cardsProto);
      playHandReq.setHand(handToPlay);

      console.log("Sending playhandRequest: ", playHandReq.toObject());
      grpc.unary(Shengji.playHand, {
        request: playHandReq,
        host: environment.grpcUrl,
        onEnd: res => {
          const { status, statusMessage, headers, message, trailers } = res;
          if (status === grpc.Code.OK && message) {
            console.log("PlayHand Response: ", message.toObject());
            this.selectedCardUIs.forEach(ui => { ui.yAdjustment = 0 })
            this.selectedCardUIs.clear();
          }
        }
      });
    }
  }
}

class Game {
  // Game metadata
  gameId;
  cardsInKitty = 8;
  gameStage = GameStage.Deal;
  trickPile : TrickPile;

  // Trump metadata
  declaredTrumps = DeclaredTrump.None;
  trumpRank = 2;
  cardRanking = new CardRanking(this.trumpRank);

  // Player metadata
  playerId;
  players : Player[] = [];
  currentPlayer = 0;
  kittyPlayer = 0;

  // UI elements
  cardMargin = -1;
  labelHeight = -1;
  deckUI;
  kittyUI;
  cardSize: any;
  width : number;
  height : number;
  playerLocations: any;

  constructor(height: number, width: number, playerId: string, gameId: string) {
    this.playerId = playerId;
    this.gameId = gameId;
    this.height = height;
    this.width = width;

    // Initialize with two decks
    this.cardMargin = height / 300;
    this.labelHeight = height / 40;
    // Seven rows layout: 1) top player hands; 2) top player winning
    // tricks; 3) top player played cards; 4) left / right player
    // hands with played cards; 5) left / right player winning cards;
    // 6) bottom player hands; 7) bottome player winning tricks.
    const minCardHeight = (height - 6 * this.cardMargin - 3 * this.labelHeight) / 7;
    // Middle player row layout: 1 face plus 24 1/5 shown hands * 2 + 3 playing card + 4 padding
    // NOTE: Worst case for bottom row layout isn't included in the calculation:
    // 1 face plus 7 1/5 shown hidden kitty + 1 face hand card
    // + 1 face winning card + 95 1/5 shown winning card + 2 padding
    // const minCardWidth = (width - 2 * this.cardMargin) / 25;
    const minCardWidth = (width - 6 * this.cardMargin) / 17;
    const originCardWidth = 69;
    const originCardHeight = 94;
    this.cardSize = {
      width: Math.min(minCardWidth, minCardHeight * originCardWidth / originCardHeight),
      height: Math.min(minCardHeight, minCardWidth * originCardHeight / originCardWidth),
      padding: Math.min(minCardWidth, minCardHeight * originCardWidth / originCardHeight) / 5,
    }
    // Create players. Note that x and y coordinates are the central
    // point between hand pile and trickWon pile.
    // For left / right player, We can have a max of 33 cards (25
    // cards + 8 kitty), so the central_x locates at (1 full face
    // card plus 32 padding)/2
    this.playerLocations = [
      {"x": this.width/2, "y": this.height - this.cardHeight() - this.cardMargin}, // bottom
      {"x": this.width - (this.cardWidth() + this.cardPadding() * 32)/2, "y": this.height/2}, // right
      {"x": this.width/2, "y": this.cardHeight() + this.cardMargin}, // top
      {"x": (this.cardWidth() + this.cardPadding() * 32)/2, "y": this.height/2} // left
    ];
  }

  addPlayer(playerName: string):void {
    const playerCounts = this.players.length;
    const newPlayer = new Player(this, playerCounts, playerName, this.playerLocations[playerCounts].x, this.playerLocations[playerCounts].y);
    this.players.push(newPlayer);
  }

  start() {
    cards.init({table: "#card-table", loop: 2, cardSize: this.cardSize});
    // Create kitty
    this.kittyUI = new cards.Hand({faceUp:true, x:this.cardWidth()/2 + 4.5*this.cardPadding(), y:this.height - this.cardWidth()/2 - this.cardPadding()})

    // Create trick pile
    this.trickPile = new TrickPile(this, this.players, this.cardRanking, this.width/2, this.height/2);
    this.deckUI = new cards.Deck({x:this.width/2, y:this.height/2});
    this.deckUI.addCards(cards.all);
    this.deckUI.render({immediate: true});
  }

  cardHeight(): number {
    return this.cardSize.height;
  }

  cardWidth(): number {
    return this.cardSize.width;
  }

  cardPadding(): number {
    return this.cardSize.padding;
  }

  renderCardDealt(playerId: string, card: CardProto) {
    console.log(`Dealing card: ${card} to player ${playerId} Deck: ${this.deckUI.length}`);
    // Manually alter the suit and rank for the last placeholder card to be
    // the one returned from backend. This is done as we don't know what
    // cards are in the deck initially.

    let player = this.players.find(player => player.name == playerId);

    this.deckUI[this.deckUI.length-1].suit = getCardUISuitFromProto(card);
    this.deckUI[this.deckUI.length-1].rank = card.getRank();
    player.handUI.addCard(this.deckUI.topCard());
    player.render({speed: 50});
  }

  renderKittyHiddenUpdate(kittyPlayerId: string, cards: Card[]) {
    let player = this.players.find(player => player.name == kittyPlayerId);
    cards.sort((a, b) => this.cardRanking.getUIRank(a) - this.cardRanking.getUIRank(b));
    this.kittyUI.addCards(resolveCardUIs(cards, player.handUI));
    this.kittyUI.render();
    player.handUI.render();
  }

  // mocking RPC: TO BE DELETED
  draw(playerIndex: number) : Card[] {
    if (this.gameStage === GameStage.Deal) {
      if (playerIndex === this.currentPlayer) {
        this.currentPlayer = (this.currentPlayer + 1) % this.players.length;
        let card = this.deckUI.topCard();
        this.players[playerIndex].handUI.addCard(card);
        this.players[playerIndex].render({speed: 100});

        if (this.deckUI.length === this.cardsInKitty) {
          this.gameStage = GameStage.DealKitty;
          this.currentPlayer = this.kittyPlayer;
        }

        return [toCard(card)];
      }
    }
    else if (this.gameStage === GameStage.DealKitty) {
      if (playerIndex === this.kittyPlayer) {
        let cards = this.deckUI.map(ui => toCard(ui));
        this.deckUI.deal(cards.length, [this.players[playerIndex].handUI]);
        this.players[playerIndex].render();

        if (this.deckUI.length === 0) {
          this.gameStage = GameStage.HideKitty;
        }

        return cards;
      }
    }
    return [Card.none];
  }

  async play(playerIndex: number, cards: Card[]) : Promise<boolean> {
    // TODO: Check that player isn't lying and actually has the cards
    cards.sort((a, b) => this.cardRanking.getUIRank(a) - this.cardRanking.getUIRank(b));

    if (this.gameStage === GameStage.Deal) {
      let that = this;
      let declareTrump = function(declaredTrump: DeclaredTrump) {
        that.declaredTrumps = declaredTrump;
        that.cardRanking.resetOrder(cards[0].suit);

        if (that.trumpRank === 2) {
          that.kittyPlayer = playerIndex;
        }

        that.players.forEach(p => p.render());

        console.log("player " + playerIndex + " declared " + Suit[that.cardRanking.trumpSuit]);
      }

       // Single trump
      if (this.declaredTrumps < DeclaredTrump.Single && cards.length === 1 && cards[0].rank === this.trumpRank) {
        declareTrump(DeclaredTrump.Single);
        return true;
      }
      // TODO: Can you revoke your own declarations?
      if (cards.length === 2 && cardsEquals(cards[0], cards[1])) {
         // Pair of trumps
        if (this.declaredTrumps < DeclaredTrump.Pair && cards[0].rank === this.trumpRank) {
            declareTrump(DeclaredTrump.Pair);
            return true;
          }
        // Pair of Jokers (TODO: should big jokers over trump small jokers? What about three player games e.g. 3 2's vs 2 Jokers?)
        if (this.declaredTrumps < DeclaredTrump.Jokers && cards[0].suit === Suit.Joker) {
            declareTrump(DeclaredTrump.Jokers);
            return true;
          }
      }
    }
    else if (this.gameStage === GameStage.HideKitty) {
      if (cards.length === this.cardsInKitty && playerIndex === this.currentPlayer) {
        this.kittyUI.addCards(resolveCardUIs(cards, this.players[this.currentPlayer].handUI));
        this.kittyUI.render();
        this.players[this.currentPlayer].handUI.render();

        this.gameStage = GameStage.Play;
        this.trickPile.initialize(this.cardRanking);
        return true;
      }
    }
    else if (this.gameStage === GameStage.Play && playerIndex === this.currentPlayer) {
      if (!this.trickPile.play(this.currentPlayer, cards)) {
        return false;
      }

      // Stage change to prevent UI issues. This is probably not strictly threadsafe.
      this.gameStage = GameStage.Busy;
      let winner = await this.trickPile.getWinner();
      this.gameStage = GameStage.Play;

      this.currentPlayer = winner ?? (this.currentPlayer + 1) % this.players.length;

      // Game end
      if (winner !== null && this.players[this.currentPlayer].handUI.length === 0) {
        let countScore = function(handUI: any[]) : number {
          let score = 0;
          for (const rank of handUI.map(ui => ui.rank)) {
            score += rank === 5 ? 5 : (rank === 10 || rank === 13) ? 10 : 0
          }
          return score;
        }

        let score = 0;
        for (const player of this.players) {
          if (player.index % 2 !== this.kittyPlayer % 2) {
            score += countScore(player.tricksWonUI);
          }
        }

        if (winner % 2 !== this.kittyPlayer % 2) {
          score += countScore(this.kittyUI) << cards.length;
        }

        console.log("Score: " + score);
      }
      return true;
    }
    return false;
  }
}
