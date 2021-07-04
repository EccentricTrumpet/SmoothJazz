import { AfterViewChecked, Component, ViewChild, ElementRef, OnInit} from '@angular/core';
import { environment } from '../../environments/environment';
import { ShengjiClient } from "proto-gen/ShengjiServiceClientPb";
import { ActivatedRoute, NavigationStart, Router } from "@angular/router";
import { COOKIE_PLAYER_NAME } from '../app.constants';
import { CookieService } from 'ngx-cookie-service';
import { AlertController } from '@ionic/angular';
import { gsap } from 'gsap';
import {
  JoinGameRequest,
  AddAIPlayerRequest,
  PlayHandRequest,
  Game as GameProto,
  Hand as HandProto,
  Card as CardProto,
  Player as PlayerProto,
  DrawCardsRequest
} from "proto-gen/shengji_pb";
declare var cards:any;

// Aliases
type Suit = CardProto.Suit;
type Rank = CardProto.Rank;
export const Suit = CardProto.Suit;
const Rank = CardProto.Rank;

// Global utilities.
const toFriendlyString = function(cardProto: CardProto): string {
  switch(cardProto.getSuit()) {
    case CardProto.Suit.SMALL_JOKER: return 'SMALL JOKER';
    case CardProto.Suit.BIG_JOKER: return 'BIG JOKER';
    case CardProto.Suit.SUIT_UNDEFINED: return 'UNDEFINED';
  }

  return `${Object.keys(CardProto.Rank).find(r => CardProto.Rank[r] === cardProto.getRank())} of ${Object.keys(CardProto.Suit).find(s => CardProto.Suit[s] === cardProto.getSuit())}`
}

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

const getCardProtoSuit = function(cardUI: any) : Suit {
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

export const cardProto = function(suit: Suit, rank: Rank) : CardProto {
  const cardProto = new CardProto();
  cardProto.setSuit(suit);
  cardProto.setRank(rank);
  return cardProto;
}

const toCardProto = function(cardUI: any) : CardProto {
  return cardProto(getCardProtoSuit(cardUI), cardUI.rank);
}

// cards and cardUIs must be in order.
const resolveCardUIs = function(cards: CardProto[], cardUIs: any[]) : any[] {
  let resolvedCardUIs: any[] = [];
  let i = 0;
  let j = 0;

  while (i < cards.length) {
    let found = false;
    while (j < cardUIs.length) {
      let cardUI = cardUIs[j++];
      let uiProto = toCardProto(cardUI);
      if (cards[i].getSuit() == uiProto.getSuit() && cards[i].getRank() == uiProto.getRank() && cardUI.selected) {
        cardUI.selected = false;
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

const renderUI = function(ui: any, immediate = false) {
  ui.prepareRender();
  for (let i = 0; i < ui.length; i++) {
    const el = ui[i];
    gsap.to(el.el, {
      x: el.targetLeft,
      y: el.targetTop,
      duration: immediate ? 0 : 0.5
    });
  }
}

@Component({
  selector: 'app-game',
  templateUrl: './game.page.html',
  styleUrls: ['./game.page.scss'],
})

export class GamePage implements AfterViewChecked, OnInit {
  @ViewChild('cardTable') tableElement: ElementRef;
  private nativeElement: any;
  private started = false;
  private gameID: string;
  private client: ShengjiClient;
  game: Game = null;
  addAIVisible: boolean = false;

  constructor(
    router: Router,
    private route: ActivatedRoute,
    private cookieService: CookieService,
    private alertController: AlertController) {
    // Close any opened dialog when route changes
    router.events.subscribe(async event => {
      if (event instanceof NavigationStart) {
        try { await this.alertController.dismiss(); } catch { }
      }
    });

    this.client = new ShengjiClient(environment.grpcUrl);

    window.addEventListener("beforeunload", (event) => {
      event.preventDefault();
      // This message does not show in modern browsers like Chrome, see https://developers.google.com/web/updates/2016/04/chrome-51-deprecations#remove_custom_messages_in_onbeforeunload_dialogs
      event.returnValue = "Exit will leave the page in a non-recoverable state, are you sure about this?";
      return event;
    });
  }

  ngOnInit() {
    this.route.params.subscribe(async params => {
      this.gameID = params['gameID'];
      console.log(`Game: ${this.gameID}`);

      if (this.cookieService.check(COOKIE_PLAYER_NAME)) {
        let playerName = this.cookieService.get(COOKIE_PLAYER_NAME);
        this.joinGame(playerName, this.gameID);
        return;
      }

      const alert = await this.alertController.create({
        header: 'Please Enter Your Name:',
        inputs: [
          {
            name: 'playerName',
            placeholder: '<Player Name>'
          },
        ],
        buttons: [
          {
            text: 'Ok',
            handler: inputData => {
              console.log(`Player name: ${inputData.playerName}`);
              this.cookieService.set(COOKIE_PLAYER_NAME, inputData.playerName);
              this.joinGame(inputData.playerName, this.gameID);
            }
          }
        ]
      });
      await alert.present();
    });
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

  async addAIPlayer() {
    const createAIRequest = new AddAIPlayerRequest();
    createAIRequest.setGameId(this.gameID);
    console.log('Adding AI Player for: '+this.gameID);

    let response = await this.client.addAIPlayer(createAIRequest, null);
    console.log(`${response.getPlayerName()} is added to the game`);
  }

  getUIIndex(playerName: string, players: PlayerProto[], player0Name: string): number {
    let player0Index = players.findIndex(p => p.getPlayerId() == player0Name);
    let playerIndex = players.findIndex(p => p.getPlayerId() == playerName);
    let uiIndex = playerIndex - player0Index;
    if (uiIndex < 0) {
      uiIndex += 4;
    }
    return uiIndex;
  }

  joinGame(playerName: string, gameID: string) {
    console.log(`${playerName} is joining game ${gameID}`);
    const joinGameRequest = new JoinGameRequest();
    joinGameRequest.setPlayerId(playerName);
    joinGameRequest.setGameId(gameID);

    this.client.joinGame(joinGameRequest)
      .on('data', (gameProto: GameProto) => {
        console.log("Current game state: ", gameProto.toObject());
        // Initialization
        if (this.game == null) {
          if (playerName == gameProto.getCreatorPlayerId()) {
            this.addAIVisible = true;
          }
          this.game = new Game(this.client, this.nativeElement.clientHeight, this.nativeElement.clientWidth, playerName, gameID);
        }
        const trumpCards = gameProto.getTrumpCards()?.getCardsList();
        const trumpCardsImgURL = trumpCards?.map(tc => {
          return "assets/cards_js_img/"+getCardUISuitFromProto(tc) + tc.getRank()+".svg";
        });
        if (trumpCards?.length > 0 && trumpCardsImgURL != this.game.trumpCardsImgURL) {
          console.log(gameProto.getTrumpPlayerId() + " declared " + trumpCards[0].getSuit()) + " as trump suit.";
          this.game.ranking.resetOrder(trumpCards[0].getSuit());
          this.game.players.forEach(p => p.render());
          this.game.trumpPlayer = gameProto.getTrumpPlayerId();
          this.game.trumpCardsImgURL = trumpCardsImgURL;
        }

        let updateId = gameProto.getUpdateId();
        if (updateId - this.game.updateId == 1)
        {
          // Render delta
          switch (gameProto.getUpdateCase()) {
            case GameProto.UpdateCase.NEW_PLAYER_UPDATE:
                let newPlayer = gameProto.getNewPlayerUpdate().getPlayerId();
                this.game.addPlayer(newPlayer, this.getUIIndex(newPlayer, gameProto.getPlayersList(), playerName));

                if (this.game.playerCount == 4) {
                  this.game.start();
                  this.addAIVisible = false;
                }
              break;
            case GameProto.UpdateCase.CARD_DEALT_UPDATE:
              let cardDealtUpdate = gameProto.getCardDealtUpdate();
              this.game.renderCardDealt(cardDealtUpdate.getPlayerId(), cardDealtUpdate.getCard())
              break;
            case GameProto.UpdateCase.KITTY_HIDDEN_UPDATE:
              let kittyHiddenUpdate = gameProto.getKittyHiddenUpdate();
              this.game.renderKittyHiddenUpdate(kittyHiddenUpdate.getKittyPlayerId(), gameProto.getKitty().getCardsList());
              break;
            default:
              console.log("Invalid update");
              break;
          }
        }
        else
        {
          // Render entire game
          console.log(`Rerender required, update ${this.game.updateId} -> ${updateId}`);

          if (this.game.gameStage == GameStage.Setup) {
            // Game hasn't started, render all player locations
            let players = gameProto.getPlayersList();

            for (let i = 0; i < players.length; i++) {
              let name = players[i].getPlayerId();
              let uiIndex = this.getUIIndex(name, players, playerName);

              this.game.addPlayer(name, uiIndex);
            }

            if (this.game.playerCount == 4) {
              this.game.start();
            }
          }
        }
        this.game.updateId = updateId;
      })
      .on('end', () => console.log('game stream closed'))
      .on('error', error => console.log(`hit an error: ${error.code} - ${error.message}`));
  }
}

enum GameStage {
  Setup,
  Deal,
  DealKitty,
  HideKitty,
  Play,
  Busy
}

export class CardRanking {
  trumpSuit: Suit = Suit.SUIT_UNDEFINED;
  trumpRank: Rank;
  uiRanks: Map<string, number> = new Map();
  functionalRanks: Map<string, number> = new Map();

  constructor(rank: Rank) {
    this.trumpRank = rank;
    this.resetOrder(this.trumpSuit);
  }

  resetOrder(suit: Suit) {
    this.trumpSuit = suit;
    const nonTrumpSuits = [Suit.SPADES, Suit.HEARTS, Suit.CLUBS, Suit.DIAMONDS].filter((s) => s !== this.trumpSuit);
    let uiRank = 0;
    let functionalRank = 0;
    let that = this;
    let setRank = function(card: CardProto, incrementFunctionalRank: boolean = true) {
      that.uiRanks.set(card.toString(), uiRank++);
      that.functionalRanks.set(card.toString(), functionalRank);
      if (incrementFunctionalRank) functionalRank++;
    }

    // Jokers
    setRank(cardProto(Suit.BIG_JOKER, Rank.RANK_UNDEFINED));
    setRank(cardProto(Suit.SMALL_JOKER, Rank.RANK_UNDEFINED));

    // Trump suit + Trump rank
    if (this.trumpSuit !== Suit.SUIT_UNDEFINED && this.trumpSuit !== Suit.BIG_JOKER && this.trumpSuit !== Suit.SMALL_JOKER) {
      setRank(cardProto(this.trumpSuit, this.trumpRank));
    }

    // Trump rank
    for (const suit of nonTrumpSuits) {
      setRank(cardProto(suit, this.trumpRank), false);
    }
    functionalRank++;

    // Trump suit
    if (this.trumpSuit !== Suit.SUIT_UNDEFINED && this.trumpSuit !== Suit.BIG_JOKER && this.trumpSuit !== Suit.SMALL_JOKER) {
      setRank(cardProto(this.trumpSuit, Rank.ACE));
      for (let rank = Rank.KING; rank >= Rank.TWO; rank--) {
        if (rank !== this.trumpRank) {
          setRank(cardProto(this.trumpSuit, rank));
        }
      }
    }

    // Others
    for (const suit of nonTrumpSuits) {
      setRank(cardProto(suit, Rank.ACE));
      for (let rank = Rank.KING; rank >= Rank.TWO; rank--) {
        if (rank !== this.trumpRank) {
          setRank(cardProto(suit, rank));
        }
      }
    }
  }

  // For display order and sorting
  getUIRank(card: CardProto) : number {
    return this.uiRanks.get(card.toString());
  }

  // For tractor and trick resolution
  getFunctionRank(card: CardProto) : number {
    return this.functionalRanks.get(card.toString());
  }

  // For determing winning tricks
  isTrump(card: CardProto) : boolean {
    let suit = card.getSuit();
    return suit === Suit.BIG_JOKER
      || suit === Suit.SMALL_JOKER
      || card.getRank() === this.trumpRank
      || (suit === this.trumpSuit && suit !== Suit.SUIT_UNDEFINED);
  }
}

class Tractor {
  highCard: CardProto;
  length: number;

  constructor(card: CardProto, length: number) {
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
  isTrump: boolean;
  length: number;
  tractorGroups: TractorGroup[] = [];
  pairs: CardProto[] = [];
  singles: CardProto[] = [];

  static invalid = new TrickFormat(Suit.SUIT_UNDEFINED, false, 0);

  constructor(suit: Suit, isTrump: boolean, length: number) {
    this.suit = suit;
    this.isTrump = isTrump;
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
    if (this.suit === Suit.SUIT_UNDEFINED) {
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
  cardsPlayedUI: any[];
  trickFormat: TrickFormat | null = null;
  winningPlayer: number | null = null;
  winningHand: TrickFormat | null = null;

  constructor(game: Game, players: Player[], x: number, y: number) {
    this.game = game;
    this.players = players;
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

  // Currently assumes cards are of the same suit, consider moving mixed suit logic here
  resolveFormat(cards: CardProto[]): TrickFormat {
    let format = new TrickFormat(cards[0].getSuit(), this.game.ranking.isTrump(cards[0]), cards.length);

    // Resolve singles and pairs
    let i = 0;
    while (i < cards.length) {
      if (i < cards.length - 1 && cards[i].toString() === cards[i+1].toString()) {
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
        && this.game.ranking.getUIRank(format.pairs[j+1]) - this.game.ranking.getUIRank(format.pairs[j]) === 1) {
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
  resolveLegalFormat(playerIndex: number, cards: CardProto[]): TrickFormat {
    // Check legality of lead
    if (this.trickFormat === null) {
      // Currently can only resolve leading plays with one suit
      if (this.game.ranking.isTrump(cards[0]))
      {
        for (const card of cards) {
          if (!this.game.ranking.isTrump(card)) {
            console.log("Cards cannot be played since more than one suit detected");
            return TrickFormat.invalid;
          }
        }
      }
      else {
        let suit = cards[0].getSuit();
        for (const card of cards) {
          if (this.game.ranking.isTrump(card) || suit !== card.getSuit()) {
            console.log("Cards cannot be played since more than one suit detected");
            return TrickFormat.invalid;
          }
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
    let suitCardsInHand: any;
    let suitTotalInHand: number;
    if (this.trickFormat.isTrump) {
      suitCardsInHand = this.players[playerIndex].handUI.map((ui: any) => toCardProto(ui))
        .filter((c: CardProto) => this.game.ranking.isTrump(c));
      suitTotalInHand = suitCardsInHand.length;
      let suitTotalInPlay = cards.filter(c =>
        this.game.ranking.isTrump(c)).length;

      if (suitTotalInPlay < Math.min(suitTotalInHand, this.trickFormat.length)) {
        console.log("Not all playable cards of the lead suit were played.");
        return TrickFormat.invalid;
      }
    }
    else {
      suitCardsInHand = this.players[playerIndex].handUI.map((ui: any) => toCardProto(ui))
        .filter((c: CardProto) => !this.game.ranking.isTrump(c) && this.trickFormat.suit === c.getSuit());
      suitTotalInHand = suitCardsInHand.length;
      let suitTotalInPlay = cards.filter(c =>
        !this.game.ranking.isTrump(c) && this.trickFormat.suit === c.getSuit()).length;

      if (suitTotalInPlay < Math.min(suitTotalInHand, this.trickFormat.length)) {
        console.log("Not all playable cards of the lead suit were played.");
        return TrickFormat.invalid;
      }
    }

    if (suitTotalInHand >= this.trickFormat.length) {
      console.log("Full follow");
      // All cards played must be of the leading suit
      let format = this.resolveFormat(cards);

      if (format === TrickFormat.invalid || format.suit === Suit.SUIT_UNDEFINED) {
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
            let compareResult = pt.highCard.toString() === st.highCard.toString() && pt.length === st.length;
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
        return new TrickFormat(Suit.SUIT_UNDEFINED, false, format.length);
      }
    }

    if (suitTotalInHand > 0 && suitTotalInHand < this.trickFormat.length) {
      // Must be a mixed format
      console.log("Partial follow, valid");
      return new TrickFormat(Suit.SUIT_UNDEFINED, false, cards.length);
    }

    if (suitTotalInHand === 0) {
      // Check for a mixed format
      for (const card of cards) {
        if (!this.game.ranking.isTrump(card)) {
          console.log("Can't follow, mixed format, valid");
          return new TrickFormat(Suit.SUIT_UNDEFINED, false, cards.length);
        }
      }

      // Must be an all trump format
      let format = this.resolveFormat(cards);
      if (!format.isTrump) {
        throw new Error("We shoud never resolve the format when non-trumps follow a leading suit");
      }

      if (this.trickFormat.isSatisfiedBy(format)) {
        console.log("Can't follow, trump format, valid");
        return format;
      }
      else {
        console.log("Can't follow, mixed trump format, valid");
        return new TrickFormat(Suit.SUIT_UNDEFINED, false, cards.length);
      }
    }

    console.log("Unknown format, invalid");
    return TrickFormat.invalid;
  }

  play(playerIndex: number, cards: CardProto[]): boolean {
    let resolvedFormat = this.resolveLegalFormat(playerIndex, cards);
    console.log(resolvedFormat);

    if (resolvedFormat === TrickFormat.invalid) {
      return false;
    }

    this.cardsPlayedUI[playerIndex].addCards(resolveCardUIs(cards, this.players[playerIndex].handUI));
    this.cardsPlayedUI[playerIndex].render();
    this.players[playerIndex].handUI.render();

    if (resolvedFormat.suit !== Suit.SUIT_UNDEFINED) {
      // Leading play
      if (this.winningHand === null) {
        this.winningHand = resolvedFormat;
        this.winningPlayer = playerIndex;
      }
      // Following play
      else {
        let that = this;
        let champDefends = function(champCards: CardProto[], challengerCards: CardProto[]) : boolean {
          champCards.sort((a, b) => that.game.ranking.getFunctionRank(a) - that.game.ranking.getFunctionRank(b));
          challengerCards.sort((a, b) => that.game.ranking.getFunctionRank(a) - that.game.ranking.getFunctionRank(b));
          for (let i = 0; i < champCards.length; i++) {
            if (that.game.ranking.getFunctionRank(challengerCards[i]) >= that.game.ranking.getFunctionRank(champCards[i])) {
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

  render() {
    this.handUI.sort((a, b) => this.game.ranking.getUIRank(toCardProto(a)) - this.game.ranking.getUIRank(toCardProto(b)));
    renderUI(this.handUI);
  }

  async act(cardUI: any, event: any) {
    // prevent context menu on right click
    event.preventDefault();

    // do nothing if player tries to play someone else's card.
    if (this.name != this.game.playerId) {
      return;
    }

    // select or deselect with click
    if (event.type === "click") {
      if (this.selectedCardUIs.has(cardUI)) {
        this.selectedCardUIs.delete(cardUI);
        cardUI.selected = false;
        renderUI(this.handUI);
        return;
      }

      cardUI.selected = true;
      this.selectedCardUIs.add(cardUI);
      renderUI(this.handUI);
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
      let response = await this.game.client.playHand(playHandReq, null);

      console.log("PlayHand Response: ", response.toObject());
      if (response.getSuccess() == false) {
        alert(response.getErrorMessage());
      }
      for (let selectedCard of this.selectedCardUIs.values()) {
        selectedCard.selected = false;
      }
      this.selectedCardUIs.clear();
      renderUI(this.handUI);
    }
  }
}

class Game {
  // Game metadata
  gameId: string;
  cardsInKitty = 8;
  gameStage = GameStage.Setup;
  trickPile: TrickPile;
  updateId =-1;

  // Trump metadata
  trumpRank: Rank = Rank.TWO;
  trumpPlayer: string = "NONE";
  trumpCardsImgURL: string[] = [];
  ranking = new CardRanking(this.trumpRank);

  // Player metadata
  playerId: string;
  players: Player[] = new Array(4).fill(null);
  playerCount = 0;
  currentPlayer = 0;
  kittyPlayer = 0;

  // UI elements
  cardMargin = -1;
  labelHeight = -1;
  deckUI;
  kittyUI;
  cardSize: any;
  width: number;
  height: number;
  playerLocations: any;

  // gRPC
  client: ShengjiClient;

  constructor(client: ShengjiClient, height: number, width: number, playerId: string, gameId: string) {
    this.client = client;

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
      padding: Math.min(minCardWidth, minCardHeight * originCardWidth / originCardHeight) / 4,
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

  addPlayer(playerName: string, index: number): void {
    this.playerCount++;
    const newPlayer = new Player(this, index, playerName, this.playerLocations[index].x, this.playerLocations[index].y);
    this.players[index] = newPlayer;
  }

  start(): void {
    cards.init({table: "#card-table", loop: 2, cardSize: this.cardSize});

    // Start game
    this.gameStage = GameStage.Deal;

    // Create kitty
    this.kittyUI = new cards.Hand({faceUp:true, x:this.cardWidth()/2 + 4.5*this.cardPadding(), y:this.height - this.cardWidth()/2 - this.cardPadding()})

    // Create trick pile
    this.trickPile = new TrickPile(this, this.players, this.width/2, this.height/2);
    this.deckUI = new cards.Deck({x:this.width/2, y:this.height/2});
    let that = this;
    this.deckUI.click(() => that.draw());
    this.deckUI.addCards(cards.all);
    renderUI(this.deckUI, true);
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

  async draw(): Promise<void> {
    const drawCardsRequest = new DrawCardsRequest();
    drawCardsRequest.setGameId(this.gameId);
    drawCardsRequest.setPlayerName(this.playerId);
    await this.client.drawCards(drawCardsRequest, null);
  }

  renderCardDealt(playerId: string, card: CardProto) {
    console.log(`Dealing card: ${toFriendlyString(card)} to player ${playerId}`);
    // Manually alter the suit and rank for the last placeholder card to be
    // the one returned from backend. This is done as we don't know what
    // cards are in the deck initially.

    let player = this.players.find(player => player.name == playerId);

    this.deckUI[this.deckUI.length-1].suit = getCardUISuitFromProto(card);
    this.deckUI[this.deckUI.length-1].rank = card.getRank();
    player.handUI.addCard(this.deckUI.topCard());
    player.render()
  }

  renderKittyHiddenUpdate(kittyPlayerId: string, cards: CardProto[]) {
    let player = this.players.find(player => player.name == kittyPlayerId);
    cards.sort((a, b) => this.ranking.getUIRank(a) - this.ranking.getUIRank(b));
    this.kittyUI.addCards(resolveCardUIs(cards, player.handUI));
    renderUI(this.kittyUI);
    renderUI(player.handUI);
  }

  async play(playerIndex: number, cards: CardProto[]) : Promise<boolean> {
    // TODO: Check that player isn't lying and actually has the cards
    cards.sort((a, b) => this.ranking.getUIRank(a) - this.ranking.getUIRank(b));
    if (this.gameStage === GameStage.Play && playerIndex === this.currentPlayer) {
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
