import { AfterViewChecked, Component, ViewChild } from '@angular/core';
declare var cards:any;

@Component({
  selector: 'app-game',
  templateUrl: './game.page.html',
  styleUrls: ['./game.page.scss'],
})

export class GamePage implements AfterViewChecked {
@ViewChild('cardTable') tableElement: any;
  started = false;

  constructor() { }

  ngAfterViewChecked() {
    if (!this.started) {
      if (this.tableElement.nativeElement.offsetHeight === 0) {
        return;
      }

      this.started = true;
      let nativeElement = this.tableElement.nativeElement;
      new Game(nativeElement.clientHeight, nativeElement.clientWidth);
    }
  }
}

enum Suit {
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

// global utilities, is this an antipattern?
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

const cardHeight = function() : number { return cards.options.cardSize.height };
const cardWidth = function() : number { return cards.options.cardSize.width };
const padding = function() : number { return cards.options.cardSize.padding };

// Card abstraction, mock type used for gRPC
class Card {
  suit: Suit;
  rank: number;

  constructor(suit: Suit, rank: number) {
    this.suit = suit;
    this.rank = rank;
  }

  static none: Card = new Card(Suit.None, 0);
  static smallJoker: Card = new Card(Suit.Joker, 1);
  static bigJoker: Card = new Card(Suit.Joker, 2);

  public toString(): string {
    return Suit[this.suit] + this.rank;
  }
}

class CardRanking {
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
  players: Player[];
  ranking: CardRanking;
  cardsPlayedUI: any[];
  trickFormat: TrickFormat | null = null;
  winningPlayer: number | null = null;
  winningHand: TrickFormat | null = null;

  constructor(players: Player[], ranking: CardRanking, x: number, y: number) {
    this.players = players;
    this.ranking = ranking;
    this.cardsPlayedUI = [players.length];
    for (let i = 0; i < this.players.length; i++) {
      let vector = [players[i].x - x, players[i].y - y];
      let magnitude = Math.sqrt(vector[0]*vector[0] + vector[1]*vector[1]);

      this.cardsPlayedUI[i] = new cards.Hand({faceUp: true,
        x:x + vector[0]*cardHeight()/magnitude,
        y:y - cardHeight()/2 + vector[1]*cardHeight()/magnitude});
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
  index: number;
  x: number;
  y: number;
  handUI;
  tricksWonUI;
  selectedCardUIs = new Set<any>();

  constructor(game: Game, index: number, x: number, y: number) {
    this.game = game;
    this.index = index;
    this.x = x;
    this.y = y;
    this.handUI = new cards.Hand({faceUp: true, x:x, y:y - cardHeight()});
    this.tricksWonUI = new cards.Hand({faceUp: true, x:x, y:y + padding()});
    let that = this;
    this.handUI.click((c, e) => that.act(c, e));
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
        cardUI.el[0].style.outline = "";
        return;
      }

      cardUI.el[0].style.outline = "dashed red";
      this.selectedCardUIs.add(cardUI);
    }
    // submit play with right click
    else if (event.type === "contextmenu") {
      // Ignore if right clicked an unselected card
      if (!this.selectedCardUIs.has(cardUI)) return;

      let cards = Array.from(this.selectedCardUIs.values()).map(ui => toCard(ui));
      cards.forEach(c => console.log(this.index + " submitting: " + c));

      if (this.game.play(this.index, cards))
      {
        this.selectedCardUIs.forEach(ui => { ui.el[0].style.outline = "" })
        this.selectedCardUIs.clear();
      }
    }
  }
}

class Game {
  // Game metadata
  cardsInKitty = 8;
  gameStage = GameStage.Deal;
  trickPile : TrickPile;

  // Trump metadata
  declaredTrumps = DeclaredTrump.None;
  trumpRank = 2;
  cardRanking = new CardRanking(this.trumpRank);

  // Player metadata
  players : Player[];
  currentPlayer = 0;
  kittyPlayer = 0;

  // UI elements
  deckUI;
  kittyUI;

  constructor(height: number, width: number) {
    // Initialize with two decks
    cards.init({table: "#card-table", loop: 2});
    this.deckUI = new cards.Deck({x:width/2, y:height/2});
    this.deckUI.addCards(cards.all);
    cards.shuffle(this.deckUI);
    this.deckUI.render({immediate: true});

    // Create players
    this.players = [
      new Player(this, 0, width/2, height - cardHeight()/2 - padding()*2),
      new Player(this, 1, width*4/5, height/2),
      new Player(this, 2, width/2, cardHeight()*1.5 + padding()),
      new Player(this, 3, width/5, height/2) ];

    // Create kitty
    this.kittyUI = new cards.Hand({faceUp:true, x:cardWidth()/2 + 4.5*padding(), y:height - cardWidth()/2 - padding()})

    // Create trick pile
    this.trickPile = new TrickPile(this.players, this.cardRanking, width/2, height/2);

    // Add listener
    let that = this;
    this.deckUI.click(() => that.draw(that.currentPlayer));
  }

  // mocking RPC
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