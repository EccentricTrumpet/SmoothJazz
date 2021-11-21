var cards = (function() {
  //The global options
  var opt = {
    cardSize: {
      width: 69,
      height: 94,
      padding: 18
    },
    table: 'body',
    cardback: 'red',
    cardsUrl: 'assets/cards_js_img/',
    loop: 1
  };
  var zIndexCounter = 1;
  var all = []; //All the cards created.

  function mouseEvent(ev) {
    var card = $(this).data('card');
    if (card.container) {
      var handler = card.container._click;
      if (handler) {
        handler.func.call(handler.context || window, card, ev);
      }
    }
  }

  function init(options) {
    if (options) {
      for (var i in options) {
        if (opt.hasOwnProperty(i)) {
          opt[i] = options[i];
        }
      }
    }

    opt.table = $(opt.table)[0];
    if ($(opt.table).css('position') == 'static') {
      $(opt.table).css('position', 'relative');
    }
    for (let l = 0; l < opt.loop * 54; l++) {
      // We rely on the backend to resolve actual cards so we just add placeholder cards here
      all.push(new Card('bj', 0, opt.table));
    }

    // Not a fan of specifying individual events. How do we handle mobile where right click might not be an option?
    $('.card').on('click', mouseEvent);
    $('.card').on('contextmenu', mouseEvent);
  }

  function Card(suit, rank, table) {
    this.init(suit, rank, table);
  }

  Card.prototype = {
    init: function(suit, rank, table) {
      this.suit = suit;
      this.rank = rank;
      this.name = suit.toUpperCase() + rank;
      this.faceUp = false;
      this.selected = false;
      let card_back = opt.cardback == 'red' ? 'cardback_red' : 'cardback_blue';
      this.el = $('<div/>').css({
        width: opt.cardSize.width,
        height: opt.cardSize.height,
        "background-image": 'url(' + opt.cardsUrl + card_back + '.svg)',
        "background-size": '100%',
        position: 'absolute',
        left: '0px',
        top: '0px',
        cursor: 'pointer'
      }).addClass('card').data('card', this).appendTo($(table));
    },

    toString: function() {
      return this.name;
    },

    rotate: function(angle) {
      $(this.el)
        .css('-webkit-transform', 'rotate(' + angle + 'deg)')
        .css('-moz-transform', 'rotate(' + angle + 'deg)')
        .css('-ms-transform', 'rotate(' + angle + 'deg)')
        .css('transform', 'rotate(' + angle + 'deg)')
        .css('-o-transform', 'rotate(' + angle + 'deg)');
    },

    updateBackgroundImg: function() {
      let shortName = this.suit == 'hidden' ? 'cardback_red' : this.suit + this.rank;
      $(this.el).css('background-image', 'url(' + opt.cardsUrl + shortName + '.svg)');
    },

    showCard: function() {
      if (this.faceUp) {
        return;
      }
      this.faceUp = true;
      this.updateBackgroundImg();
    },

    hideCard: function() {
      if (!this.faceUp) {
        return;
      }
      this.faceUp = false;
      let card_back = opt.cardback == 'red' ? 'cardback_red' : 'cardback_blue';
      $(this.el).css('background-image', 'url(' + opt.cardsUrl + card_back + '.svg)');
      this.rotate(0);
    },

    moveToFront: function() {
      $(this.el).css('z-index', zIndexCounter++);
    }
  };

  function Container() { }

  Container.prototype = new Array();
  Container.prototype.extend = function(obj) {
    for (var prop in obj) {
      this[prop] = obj[prop];
    }
  }
  Container.prototype.extend({
    addCard: function(card) {
      this.addCards([card]);
    },

    addCards: function(cards) {
      for (var i = 0; i < cards.length; i++) {
        var card = cards[i];
        if (card.container) {
          card.container.removeCard(card);
        }
        this.push(card);
        card.container = this;
      }
    },

    removeCard: function(card) {
      for (var i = 0; i < this.length; i++) {
        if (this[i] == card) {
          this.splice(i, 1);
          return true;
        }
      }
      return false;
    },

    init: function(options) {
      options = options || {};
      this.x = options.x || $(opt.table).width() / 2;
      this.y = options.y || $(opt.table).height() / 2;
      this.faceUp = options.faceUp;
    },

    click: function(func, context) {
      this._click = {
        func: func,
        context: context
      };
    },

    mousedown: function(func, context) {
      this._mousedown = {
        func: func,
        context: context
      };
    },

    mouseup: function(func, context) {
      this._mouseup = {
        func: func,
        context: context
      };
    },

    prepareRender: function(options) {
      options = options || {};
      this.calcPosition(options);
      for (var i = 0; i < this.length; i++) {
        var card = this[i];
        zIndexCounter++;
        card.moveToFront();
        if (this.faceUp) {
          card.showCard();
        } else {
          card.hideCard();
        }
      }
    },

    topCard: function() {
      return this[this.length - 1];
    },

    toString: function() {
      return 'Container';
    }
  });

  function Deck(options) {
    this.init(options);
  }

  Deck.prototype = new Container();
  Deck.prototype.extend({
    calcPosition: function(options) {
      options = options || {};
      var left = Math.round(this.x - opt.cardSize.width / 2, 0);
      var top = Math.round(this.y - opt.cardSize.height / 2, 0);
      var condenseCount = 6;
      for (var i = 0; i < this.length; i++) {
        if (i > 0 && i % condenseCount == 0) {
          top -= 1;
          left -= 1;
        }
        this[i].targetTop = top;
        this[i].targetLeft = left;
      }
    },

    toString: function() {
      return 'Deck';
    },
  });

  function Hand(options) {
    this.init(options);
  }
  Hand.prototype = new Container();
  Hand.prototype.extend({
    calcPosition: function(options) {
      options = options || {};
      var width = opt.cardSize.width + (this.length - 1) * opt.cardSize.padding;
      var left = Math.round(this.x - width / 2);
      var top = Math.round(this.y - opt.cardSize.height / 2, 0);
      for (var i = 0; i < this.length; i++) {
        this[i].targetTop = this[i].selected ? top - opt.cardSize.height/2 : top;
        this[i].targetLeft = left + i * opt.cardSize.padding;
      }
    },

    toString: function() {
      return 'Hand';
    }
  });

  return {
    init: init,
    all: all,
    Card: Card,
    Deck: Deck,
    Hand: Hand,
  };
})();
