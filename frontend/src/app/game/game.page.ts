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
    case CardProto.Suit.SUIT_UNDEFINED: return 'hidden';
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
    case "hidden": return CardProto.Suit.SUIT_UNDEFINED;
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
const resolveCardUIs = function(cards: CardProto[], cardUIs: any[], fromCurrentPlayer: boolean) : any[] {
  let resolvedCardUIs: any[] = [];
  let i = 0;
  let j = 0;

  while (i < cards.length) {
    let found = false;
    while (j < cardUIs.length) {
      let cardUI = cardUIs[j++];
      if (cardUI.suit == 'hidden') {
        console.assert(fromCurrentPlayer == false, 'Current player must not have hidden cards!');
        cardUI.suit = getCardUISuitFromProto(cards[i]);
        cardUI.rank = cards[i].getRank();
        cardUI.updateBackgroundImg();
        found = true;
        resolvedCardUIs.push(cardUI);
        break;
      }
      let uiProto = toCardProto(cardUI);
      if (cards[i].getSuit() == uiProto.getSuit() && cards[i].getRank() == uiProto.getRank() && (cardUI.selected || !fromCurrentPlayer)) {
        cardUI.selected = false;
        found = true;
        resolvedCardUIs.push(cardUI);
        break;
      }
    }
    if (!found) {
      console.log('ERROR: Cannot find card from UI!!!');
      let error_msg = `Could not resolve ${toFriendlyString(cards[i])}; Cards length: ${cards.length}; fromCurrentPlayer is ${fromCurrentPlayer}. CardUIs: ${cardUIs}`;
      console.log(error_msg);
      console.log(cardUIs);
      throw Error(error_msg);
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
    createAIRequest.setAiType(AddAIPlayerRequest.AIType.AARON_AI);
    console.log('Adding AI Player for: '+this.gameID);

    let response = await this.client.addAIPlayer(createAIRequest, null);
    console.log(`${response.getPlayerName()} is added to the game`);
  }

  getUIIndex(playerName: string, players: PlayerProto[], player0Name: string): number {
    let player0Index = players.findIndex(p => p.getPlayerName() == player0Name);
    let playerIndex = players.findIndex(p => p.getPlayerName() == playerName);
    let uiIndex = playerIndex - player0Index;
    if (uiIndex < 0) {
      uiIndex += 4;
    }
    return uiIndex;
  }

  joinGame(playerName: string, gameID: string) {
    console.log(`${playerName} is joining game ${gameID}`);
    const joinGameRequest = new JoinGameRequest();
    joinGameRequest.setPlayerName(playerName);
    joinGameRequest.setGameId(gameID);

    this.client.joinGame(joinGameRequest)
      .on('data', (gameProto: GameProto) => {
        console.log("Current game state: ", gameProto.toObject());
        // Initialization
        if (this.game == null) {
          if (playerName == gameProto.getCreatorPlayerName()) {
            this.addAIVisible = true;
          }
          this.game = new Game(this.client, this.nativeElement.clientHeight, this.nativeElement.clientWidth, playerName, gameID);
        }
        this.game.kittyPlayer = gameProto.getKittyPlayerName();
        const trumpCards = gameProto.getTrumpCards()?.getCardsList();
        const trumpCardsImgURL = trumpCards?.map(tc => {
          return "assets/cards_js_img/"+getCardUISuitFromProto(tc) + tc.getRank()+".svg";
        });
        if (trumpCards?.length > 0 && JSON.stringify(trumpCardsImgURL) !== JSON.stringify(this.game.trumpCardsImgURL)) {
          console.log(`${gameProto.getTrumpPlayerName()} declared ${toFriendlyString(trumpCards[0])} as trump.`);
          this.game.ranking.resetOrder(trumpCards[0].getSuit());
          this.game.players.forEach(p => p.render());
          this.game.trumpPlayer = gameProto.getTrumpPlayerName();
          this.game.trumpCardsImgURL = trumpCardsImgURL;
        }

        let updateId = gameProto.getUpdateId();
        if (updateId - this.game.updateId == 1)
        {
          // Render delta
          switch (gameProto.getUpdateCase()) {
            case GameProto.UpdateCase.NEW_PLAYER_UPDATE:
                let newPlayer = gameProto.getNewPlayerUpdate().getPlayerName();
                this.game.addPlayer(newPlayer, this.getUIIndex(newPlayer, gameProto.getPlayersList(), playerName));

                if (this.game.playerCount == 4) {
                  this.game.start();
                  this.addAIVisible = false;
                }
              break;
            case GameProto.UpdateCase.CARD_DEALT_UPDATE:
              let cardDealtUpdate = gameProto.getCardDealtUpdate();
              this.game.renderCardDealt(cardDealtUpdate.getPlayerName(), cardDealtUpdate.getCard())
              break;
            case GameProto.UpdateCase.KITTY_HIDDEN_UPDATE:
              let kittyHiddenUpdate = gameProto.getKittyHiddenUpdate();
              this.game.renderKittyHiddenUpdate(kittyHiddenUpdate.getKittyPlayerName(), gameProto.getKitty().getCardsList(), playerName);
              break;
            case GameProto.UpdateCase.TRICK_PLAYED_UPDATE:
              let trickPlayedUpdate = gameProto.getTrickPlayedUpdate();
              this.game.renderTrickPlayedUpdate(trickPlayedUpdate.getPlayerName(),
                                                trickPlayedUpdate.getHandPlayed().getCardsList());
              let currentRoundTricks = gameProto.getPlayersList().map((player) => (
                player.getCurrentRoundTrick())).filter(trick => trick?.getCardsList()?.length > 0);
              if (currentRoundTricks.length == 4) {
                this.game.score = gameProto.getTotalScore();
                this.game.renderTrickWonAnimation(gameProto.getNextTurnPlayerName());
              }
              break;
            default:
              console.log("Invalid update: "+gameProto.getUpdateCase());
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
              let name = players[i].getPlayerName();
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

// UI ranking
export class Ranking {
  trumpSuit: Suit = Suit.SUIT_UNDEFINED;
  trumpRank: Rank;
  ranking: Map<string, number> = new Map();

  constructor(rank: Rank) {
    this.trumpRank = rank;
    this.resetOrder(this.trumpSuit);
  }

  resetOrder(suit: Suit) {
    this.trumpSuit = suit;
    const nonTrumpSuits = [Suit.SPADES, Suit.HEARTS, Suit.CLUBS, Suit.DIAMONDS].filter((s) => s !== this.trumpSuit);
    let uiRanking = 0;
    let that = this;
    let setRank = function(card: CardProto) {
      that.ranking.set(card.toString(), uiRanking++);
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
      setRank(cardProto(suit, this.trumpRank));
    }

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
  getRank(card: CardProto) : number {
    return this.ranking.get(card.toString());
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

class TrickPile {
  game: Game;
  players: Player[];
  cardsPlayedUI: Map<string, any> = new Map();
  winningPlayer: number | null = null;

  constructor(game: Game, players: Player[], x: number, y: number) {
    this.game = game;
    this.players = players;
    for (let i = 0; i < players.length; i++) {
      let vector = [players[i].x - x, players[i].y - y];
      let magnitude = Math.sqrt(vector[0]*vector[0] + vector[1]*vector[1]);
      this.cardsPlayedUI.set(players[i].name, new cards.Hand({faceUp: true,
        x:x + vector[0]*this.game.cardWidth()/magnitude,
        y:y + vector[1]*this.game.cardHeight()/magnitude
      }));
    }
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
    this.handUI.sort((a, b) => this.game.ranking.getRank(toCardProto(a)) - this.game.ranking.getRank(toCardProto(b)));
    // console.log(`player ${this.name} handUI: ${JSON.stringify(this.handUI)}`);
    console.log(`player ${this.name} handUI: ${this.handUI}`);
    console.log(this.handUI);
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
      playHandReq.setPlayerName(this.game.playerId);
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
      if (response.getErrorMessage() != "") {
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
  score: number = 0;

  // Trump metadata
  trumpRank: Rank = Rank.TWO;
  trumpPlayer: string = "NONE";
  trumpCardsImgURL: string[] = [];
  ranking = new Ranking(this.trumpRank);

  // Player metadata
  playerId: string;
  players: Player[] = new Array(4).fill(null);
  playerCount = 0;
  kittyPlayer: string;

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
    console.log(`Finished overwriting top card`);
    player.handUI.addCard(this.deckUI.topCard());
    console.log(`Finished adding card`);
    player.render()
    console.log(`Finished rendering~`);
  }

  renderTrickPlayedUpdate(playerId: string, cards: CardProto[]) {
    console.log(`Player ${playerId} plays ${cards}`);
    let player = this.players.find(player => player.name == playerId);
    let cardUIs = resolveCardUIs(cards, player.handUI, false);
    let trickPlayedUI = this.trickPile.cardsPlayedUI.get(playerId);
    trickPlayedUI.addCards(cardUIs);
    renderUI(player.handUI);
    renderUI(trickPlayedUI);
  }

  async renderTrickWonAnimation(winnerPlayerName: string) {
    console.log(`Player ${winnerPlayerName} won!`);
    let winnerPlayer = this.players.find(player => player.name == winnerPlayerName);
    let winnerUI = winnerPlayer.tricksWonUI;
    let cards = [];
    for (let play of this.trickPile.cardsPlayedUI.values()) {
      for (let i = 0; i < play.length; i++) {
        cards.push(play[i]);
      }
    }
    winnerUI.addCards(cards);

    // Pause so user can see all cards. Note that this needs to be faster
    // than people's reaction time in production, otherwise, someone may play
    // new round before the previous round's animation finishes.
    await new Promise(r => setTimeout(r, 500));
    renderUI(winnerUI);
  }

  renderKittyHiddenUpdate(kittyPlayerName: string, cards: CardProto[], playerName: string) {
    let player = this.players.find(player => player.name == kittyPlayerName);
    cards.sort((a, b) => this.ranking.getRank(a) - this.ranking.getRank(b));
    let cardUIs = resolveCardUIs(cards, player.handUI, playerName == kittyPlayerName);
    this.kittyUI.addCards(cardUIs);
    renderUI(this.kittyUI);
    renderUI(player.handUI);
  }
}
