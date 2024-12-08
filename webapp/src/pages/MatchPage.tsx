import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { useLocation, useParams } from "react-router-dom";
import { Manager, Socket } from "socket.io-client";
import { debounce } from "lodash";
import { Card, ControllerInterface } from "../abstractions";
import { Position, Size, Zone } from "../abstractions/bounds";
import {
  BoardState,
  CardState,
  GameState,
  OptionsState,
  PlayerState,
  TrumpState } from "../abstractions/states";
import {
  CardInfo,
  DrawRequest,
  DrawResponse,
  StartResponse,
  JoinRequest,
  JoinResponse,
  KittyRequest,
  MatchResponse,
  BidRequest,
  BidResponse,
  KittyResponse,
  PlayRequest,
  PlayResponse,
  TrickResponse,
  EndResponse,
  NextRequest} from "../abstractions/messages";
import { CenterZone, ControlZone, PlayerZone } from "../components";
import { GamePhase, Suit } from "../abstractions/enums";
import { Constants } from "../Constants";

function partition<T>(array: T[], condition: (element: T) => boolean) : [T[], T[]] {
  return array.reduce(([pass, fail], elem) => {
    return condition(elem) ? [[...pass, elem], fail] : [pass, [...fail, elem]];
  }, [[], []] as [T[], T[]]);
}

export default function MatchPage() {
  // React states
  const { id } = useParams();
  const { state } = useLocation();

  // API states
  const [socket, setSocket] = useState<Socket>();

  // UI states
  const [zone, setZone] = useState(new Zone(
    new Position(0, 0),
    new Size(window.innerWidth, window.innerHeight)
  ));
  const deckZone = new Zone(
    new Position(
      zone.center().x - Constants.cardWidth/2,
      zone.center().y - Constants.cardHeight/2
    ),
    new Size(Constants.cardWidth, Constants.cardHeight)
  );;

  // Game states
  const matchId = Number(id);
  const name: string = state.name;
  const [playerId, setPlayerId] = useState(-1);
  const [gameState, setGameState] = useState(new GameState());
  const [boardState, setBoardState] = useState(new BoardState());
  const [trumpState, setTrumpState] = useState(new TrumpState(0, 0));

  // Assume the new player sits in the South seat upon joining
  const matchResponse: MatchResponse = state.matchResponse;
  const [players, setPlayers] = useState(matchResponse.players);
  const options = new OptionsState("red.png");

  // Establish window size
  useEffect(() => {
    const handleResize = debounce(() => {
      setZone(new Zone(
        new Position(0, 0),
        new Size(window.innerWidth, window.innerHeight)
      ));
    }, 1);
    window.addEventListener("resize", handleResize);
    return () => {
      handleResize.cancel();
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  // Establish socket connection
  useEffect(() => {
    console.log('establishing connection')

    const manager = new Manager("localhost:5001")
    const matchSocket = manager.socket("/match")

    matchSocket.on("disconnect", () => {
      console.log('socket disconnected');
    });

    matchSocket.on("connect", () => {
      setSocket(matchSocket)
      console.log('socket connected');
    });

    return () => {
      // Teardown
      matchSocket.off("connect")
      matchSocket.disconnect();
      matchSocket.off("disconnect")
    };
  }, []);

  // Configure messages
  useEffect(() => {
    if (socket) {
      let currentPlayerId = -1;
      // Receive messages
      socket.on("data", (data) => {
        console.log(`raw join response: ${JSON.stringify(data)}`);
      });

      socket.on("leave", (player_name) => {
        console.log(`${player_name} has left the match`);
      });

      socket.on("join", (response) => {
        console.log(`raw join response: ${JSON.stringify(response)}`);
        const joinResponse = new JoinResponse(response);

        if (joinResponse.name === name) {
          currentPlayerId = joinResponse.id;
          setPlayerId(joinResponse.id);
        }

        // Need to use callback to ensure atomicity
        setPlayers(prevPlayers => [...prevPlayers, new PlayerState(
          joinResponse.id,
          joinResponse.name,
          PlayerState.getSeat(joinResponse.id, matchResponse.seatOffset, matchResponse.numPlayers)
        )]);
      });

      socket.on("start", (response) => {
        console.log(`raw start response: ${JSON.stringify(response)}`);
        const startResponse = new StartResponse(response);

        setGameState(new GameState(startResponse.activePlayerId, startResponse.phase));
        setTrumpState(new TrumpState(startResponse.deckSize, startResponse.gameRank));
        setBoardState(new BoardState(
          Array(startResponse.deckSize).fill('').map((_, i) =>
            new Card(-(1 + i), Suit.Unknown, 0, new CardState(
              true,
              false,
              0,
              new Position(0, 0),
              new Position(i/3, 0)
            ))
          )
        ));
        setPlayers(prevPlayers => prevPlayers.map(player => new PlayerState(player.id, player.name, player.seat)));
      });

      socket.on("draw", (response) => {
        console.log(`raw draw response: ${JSON.stringify(response)}`);
        const drawResponse = new DrawResponse(response);

        let drawnCards: Card[];
        setBoardState(prevBoardState => {
          drawnCards = prevBoardState.deck.slice(-drawResponse.cards.length);
          return new BoardState(
            prevBoardState.deck.slice(0, -drawResponse.cards.length),
            prevBoardState.kitty,
            prevBoardState.discard,
            prevBoardState.score
          )
        });

        // Add new cards to player's hand
        setPlayers(prevPlayers => prevPlayers.map((player) => {
          let newPlayerState: PlayerState;
          if (player.id === drawResponse.id) {
            for (let i = 0; i < drawnCards.length; i++) {
              drawnCards[i].prepareState();
              drawnCards[i].id = drawResponse.cards[i].id;
              if (drawResponse.cards[i].suit === Suit.Unknown) {
                drawnCards[i].state.facedown = true;
              }
              else {
                drawnCards[i].state.facedown = false;
                drawnCards[i].suit = drawResponse.cards[i].suit;
                drawnCards[i].rank = drawResponse.cards[i].rank;
              }
            }

            newPlayerState = new PlayerState(player.id, player.name, player.seat, [...player.hand, ...drawnCards], player.playing);
          }
          else {
            newPlayerState = player;
          }

          // Withdraw any bids in preparation for game start
          if (drawResponse.phase === GamePhase.Kitty && newPlayerState.playing.length > 0) {
            for (const card of newPlayerState.playing) {
              card.prepareState();
              card.state.facedown = !matchResponse.debug && player.id !== currentPlayerId;
            }
            newPlayerState.hand = [...newPlayerState.hand, ...newPlayerState.playing];
            newPlayerState.playing = [];
          }

          return newPlayerState;
        }));

        // Set new game state
        setGameState(_ => new GameState(drawResponse.activePlayerId, drawResponse.phase));
      });

      socket.on("bid", (response) => {
        console.log(`raw bid response: ${JSON.stringify(response)}`);
        const bidResponse = new BidResponse(response);
        const trumpCards = new Map<number, CardInfo>();
        for (const card of bidResponse.trumps) {
          trumpCards.set(card.id, card);
        }

        // Move bid to the play zone and let previous bidder pick up their cards
        setPlayers(prevPlayers => prevPlayers.map((player) => {
          if (player.id === bidResponse.playerId) {
            const [newPlaying, newHand] = partition(player.hand, card => trumpCards.has(card.id));

            for (const card of newPlaying) {
              const trumpInfo = trumpCards.get(card.id);
              card.prepareState();
              card.state.selected = false;
              card.state.facedown = false;
              card.suit = trumpInfo!.suit;
              card.rank = trumpInfo!.rank;
            }

            return new PlayerState(player.id, player.name, player.seat, newHand, [...player.playing, ...newPlaying]);
          }
          else if (player.playing.length > 0) {
            for (const card of player.playing) {
              card.prepareState();
              card.state.facedown = !matchResponse.debug && player.id !== currentPlayerId;
            }
            return new PlayerState(player.id, player.name, player.seat, [...player.hand, ...player.playing]);
          }
          else {
            return player;
          }
        }));

        setTrumpState(prevTrumpState => new TrumpState(
          prevTrumpState.numCards,
          prevTrumpState.trumpRank,
          bidResponse.trumps[0].suit));
      });

      socket.on("kitty", (response) => {
        console.log(`raw kitty response: ${JSON.stringify(response)}`);
        const kittyResponse = new KittyResponse(response);
        const kitty: Card[] = [];

        // Add new cards to player's hand
        setPlayers(prevPlayers => prevPlayers.map((player) => {
          if (player.id === kittyResponse.playerId) {
            const [newKitty, newHand] = partition(player.hand, (card) => {
              return kittyResponse.cards.some((kittyCard) => kittyCard.id === card.id);
            });

            for (const card of newKitty) {
              const newCard = card.clone()
              newCard.state.selected = false;
              newCard.state.facedown = true;
              newCard.state.rotate = 0;
              kitty.push(newCard);
            }

            return new PlayerState(player.id, player.name, player.seat, newHand, player.playing);
          }
          else {
            return player;
          }
        }));

        setBoardState(prevBoardState => new BoardState(
          prevBoardState.deck,
          kitty,
          prevBoardState.discard,
          prevBoardState.score
        ));

        // Set new game state
        setGameState(prevGameState => new GameState(prevGameState.activePlayerId, kittyResponse.phase));
      });

      socket.on("play", (response) => {
        console.log(`raw play response: ${JSON.stringify(response)}`);
        const playResponse = new PlayResponse(response);
        const playCards = new Map<number, CardInfo>();
        for (const card of playResponse.cards) {
          playCards.set(card.id, card);
        }

        setPlayers(prevPlayers => prevPlayers.map((player) => {
          if (player.id === playResponse.playerId) {
            const [newPlaying, newHand] = partition(player.hand, card => playCards.has(card.id));

            for (const card of newPlaying) {
              const cardInfo = playCards.get(card.id);
              card.prepareState();
              card.state.selected = false;
              card.state.facedown = false;
              card.suit = cardInfo!.suit;
              card.rank = cardInfo!.rank;
            }

            return new PlayerState(player.id, player.name, player.seat, newHand, [...player.playing, ...newPlaying]);
          }

          else {
            return player;
          }
        }));

        // Set new game state
        setGameState(prevGameState => new GameState(playResponse.activePlayerId, prevGameState.phase));
      });

      socket.on("trick", async (response) => {
        console.log(`raw trick response: ${JSON.stringify(response)}`);
        const trickResponse = new TrickResponse(response);
        const playCards = new Map<number, CardInfo>();
        for (const card of trickResponse.play.cards) {
          playCards.set(card.id, card);
        }

        setPlayers(prevPlayers => prevPlayers.map((player) => {
          if (player.id === trickResponse.play.playerId) {
            const [newPlaying, newHand] = partition(player.hand, card => playCards.has(card.id));

            for (const card of newPlaying) {
              const cardInfo = playCards.get(card.id);
              card.prepareState();
              card.state.selected = false;
              card.state.facedown = false;
              card.suit = cardInfo!.suit;
              card.rank = cardInfo!.rank;
            }

            return new PlayerState(player.id, player.name, player.seat, newHand, [...player.playing, ...newPlaying]);
          }
          else {
            return player;
          }
        }));

        await new Promise(f => setTimeout(f, 1000));

        const discardedCards: Card[] = [];

        // Remove played cards from players
        setPlayers(prevPlayers => {
          const newPlayers = prevPlayers.map((player) => {
            for (const card of player.playing) {
              const discardedCard = card.clone();
              discardedCard.state.rotate = 0;
              discardedCards.push(discardedCard);
            }

            return new PlayerState(player.id, player.name, player.seat, player.hand);
          });

          // Some state update mechanism is requiring this to be inside of setPlayers
          // Otherwise the discarded cards aren't appended correctly

          // Add discarded cards to pile and update score
          setBoardState(prevBoardState => new BoardState(
            prevBoardState.deck,
            prevBoardState.kitty,
            [...prevBoardState.discard, ...discardedCards],
            trickResponse.score
          ));

          return newPlayers;
        });

        // Set new game state
        setGameState(prevGameState => new GameState(trickResponse.activePlayerId, prevGameState.phase));
      });

      socket.on("end", async (response) => {
        console.log(`raw end response: ${JSON.stringify(response)}`);
        const endResponse = new EndResponse(response);
        const playCards = new Map<number, CardInfo>();
        for (const card of endResponse.trick.play.cards) {
          playCards.set(card.id, card);
        }

        setPlayers(prevPlayers => prevPlayers.map((player) => {
          if (player.id === endResponse.trick.play.playerId) {
            const [newPlaying, newHand] = partition(player.hand, card => playCards.has(card.id));

            for (const card of newPlaying) {
              const cardInfo = playCards.get(card.id);
              card.prepareState();
              card.state.selected = false;
              card.state.facedown = false;
              card.suit = cardInfo!.suit;
              card.rank = cardInfo!.rank;
            }

            return new PlayerState(player.id, player.name, player.seat, newHand, [...player.playing, ...newPlaying]);
          }
          else {
            return player;
          }
        }));

        await new Promise(f => setTimeout(f, 1000));

        const discardedCards: Card[] = [];

        // Remove played cards from players
        setPlayers(prevPlayers => {
          const newPlayers = prevPlayers.map((player) => {
            for (const card of player.playing) {
              const discardedCard = card.clone();
              discardedCard.state.rotate = 0;
              discardedCards.push(discardedCard);
            }

            return new PlayerState(player.id, player.name, player.seat, player.hand);
          });

          // Some state update mechanism is requiring this to be inside of setPlayers
          // Otherwise the discarded cards aren't appended correctly

          // Add discarded cards to pile and update score
          setBoardState(prevBoardState => new BoardState(
            prevBoardState.deck,
            prevBoardState.kitty,
            [...prevBoardState.discard, ...discardedCards],
            endResponse.trick.score
          ));

          return newPlayers;
        });

        // Set new game state
        setGameState(_ => new GameState(endResponse.trick.activePlayerId, endResponse.phase));

        await new Promise(f => setTimeout(f, 1000));

        // Display kitty
        setPlayers(prevPlayers => {
          const kitty: Card[] = [];
          const kittyCards = new Map<number, CardInfo>();
          for (const card of endResponse.kitty) {
            kittyCards.set(card.id, card);
          }

          const newPlayers = prevPlayers.map((player) => {
            if (player.id === endResponse.kittyId) {
              // Add discarded cards to pile and update score
              setBoardState(prevBoardState => {
                for (const card of prevBoardState.kitty) {
                  const kittyInfo = kittyCards.get(card.id);
                  card.prepareState();
                  card.state.facedown = false;
                  card.suit = kittyInfo!.suit;
                  card.rank = kittyInfo!.rank;
                  kitty.push(card);
                }
                return new BoardState(
                  prevBoardState.deck,
                  [],
                  prevBoardState.discard,
                  endResponse.score
                );
              });

              return new PlayerState(player.id, player.name, player.seat, player.hand, kitty);
            }

            return player;
          });

          // Some state update mechanism is requiring this to be inside of setPlayers
          // Otherwise the discarded cards aren't appended correctly

          return newPlayers;
        });

        setGameState(_ => new GameState(endResponse.leadId, endResponse.phase));
      });

      // Join match
      socket.emit("join", new JoinRequest(Number(matchId), name));

      return () => {
        // Teardown
        socket.emit("leave", name, matchId);
        socket.off("end");
        socket.off("trick");
        socket.off("play");
        socket.off("kitty");
        socket.off("bid");
        socket.off("draw");
        socket.off("start");
        socket.off("join");
        socket.off("leave");
        socket.off("data");
      };
    }
  // Must not depend on any mutable states
  }, [socket, name, matchId, matchResponse]);

  class Controller implements ControllerInterface {
    onShow(playerId: number) {
      const cards: CardInfo[] = [];
      for (const card of players[playerId].hand) {
        if (card.state.selected) {
          cards.push(new CardInfo(card.id, card.suit, card.rank))
        }
      }
      socket?.emit("bid", new BidRequest(matchId, playerId, cards));
    }

    onDraw() {
      if (matchResponse.debug || playerId === gameState.activePlayerId) {
        socket?.emit("draw", new DrawRequest(matchId, gameState.activePlayerId));
      }
    }

    onSelect(selectedCard: Card) {
      const nextPlayers = players.map((player) => {
        let updated = false;

        const nextHand = player.hand.map((card) => {
          if (card.id === selectedCard.id) {
            const nextCard = card.clone();
            nextCard.state.selected = !card.state.selected;
            updated = true;
            return nextCard;
          }
          else {
            return card;
          }
        });

        return updated ? new PlayerState(player.id, player.name, player.seat, nextHand, player.playing) : player;
      });
      setPlayers(nextPlayers);
    }

    onHide(playerId: number) {
      const cards: CardInfo[] = [];
      for (const card of players[playerId].hand) {
        if (card.state.selected) {
          cards.push(new CardInfo(
            card.id,
            card.suit,
            card.rank
          ))
        }
      }
      socket?.emit("kitty", new KittyRequest(matchId, playerId, cards));
    };

    onPlay = (playerId: number) => {
      const cards: CardInfo[] = [];
      for (const card of players[playerId].hand) {
        if (card.state.selected) {
          cards.push(new CardInfo(
            card.id,
            card.suit,
            card.rank
          ))
        }
      }
      socket?.emit("play", new PlayRequest(matchId, playerId, cards));
    };

    onNext = (playerId: number) => {
      setGameState(prevGameState => new GameState(prevGameState.activePlayerId, GamePhase.Waiting));
      socket?.emit("next", new NextRequest(matchId, playerId));
    };
  }

  const gameController = new Controller();

  return (
    !socket ? (
      <p>Loading ...</p>
    ) : (
    <motion.div style={{
      display: "grid",
      placeContent: "center",
      width: "100vw",
      height: "100vh"
    }}>
      <ControlZone
        parentZone={zone}
        gameState={gameState}
        playerId={playerId}
        controller={gameController}
        debug={matchResponse.debug} />
      <CenterZone
        board={boardState}
        deckZone={deckZone}
        options={options}
        controller={gameController} />
      { players.map((player) => {
        return <PlayerZone
          key={player.id}
          player={player}
          activePlayerId={gameState.activePlayerId}
          trumpState={trumpState}
          parentZone={zone}
          options={options}
          controller={gameController} />
      })}
    </motion.div>
  ));
}
