import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { useLocation, useParams } from "react-router-dom";
import { Manager, Socket } from "socket.io-client";
import { debounce } from "lodash";
import { Card, ControllerInterface } from "../abstractions";
import { Position, Size, Zone } from "../abstractions/bounds";
import { GamePhase } from "../abstractions/enums";
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
  NextRequest } from "../abstractions/messages";
  import { BoardState, GameState, OptionsState, PlayerState, TrumpState } from "../abstractions/states";
import { CenterZone, ControlZone, PlayerZone } from "../components";
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
  const options = new OptionsState("red.png");
  const matchId = Number(id);
  const { name, matchResponse }: {name: string, matchResponse: MatchResponse} = state;

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
  );

  // Game states
  const [playerId, setPlayerId] = useState(-1);
  const [gameState, setGameState] = useState(new GameState());
  const [boardState, setBoardState] = useState(new BoardState());
  const [trumpState, setTrumpState] = useState(new TrumpState(0, 0));
  const [players, setPlayers] = useState(matchResponse.players);
  const [socket, setSocket] = useState<Socket>();

  // Establish window size
  useEffect(() => {
    const handleResize = debounce(() => setZone(new Zone(
      new Position(0, 0),
      new Size(window.innerWidth, window.innerHeight)
    )), 1);
    window.addEventListener("resize", handleResize);
    return () => {
      handleResize.cancel();
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  // Establish socket connection
  useEffect(() => {
    console.log('establishing connection')
    const matchSocket = new Manager(process.env.REACT_APP_API_URL || '').socket("/match");

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

  // Configure socket messages
  useEffect(() => {
    if (socket) {
      // States and helpers
      let thisPlayerId = -1;

      const createCardDict = (cards: CardInfo[]) => {
        const dict = new Map<number, CardInfo>();
        cards.forEach(card => dict.set(card.id, card));
        return dict;
      }

      const playCards = (cards: CardInfo[], playerId: number) => {
        const playCards = createCardDict(cards);

        setPlayers(prevPlayers => prevPlayers.map((player) => {
          if (player.id === playerId) {
            const [newPlaying, newHand] = partition(player.hand, card => playCards.has(card.id));
            newPlaying.forEach(card => card.updateInfo(playCards.get(card.id)!));
            return new PlayerState(player.id, player.name, player.seat, newHand, [...player.playing, ...newPlaying]);
          }
          return player;
        }));
      }

      const cleanupTrickAsync = async (score: number) => {
        await new Promise(f => setTimeout(f, 1000));

        // Remove played cards from players
        setPlayers(prevPlayers => {
          const discards: Card[] = [];
          const newPlayers = prevPlayers.map((player) => {
            for (const card of player.playing) {
              card.resetState();
              card.state.rotate = 0;
              discards.push(card);
            }
            return new PlayerState(player.id, player.name, player.seat, player.hand);
          });

          // Add discarded cards to pile and update score
          setBoardState(pState => new BoardState(pState.deck, pState.kitty, [...pState.discard, ...discards], score));
          return newPlayers;
        });
      }

      const withdrawPlaying = (ignorePlayer: number | undefined = undefined) => {
        setPlayers(prevPlayers => prevPlayers.map((player) => {
          if (player.id !== ignorePlayer && player.playing.length > 0) {
            for (const card of player.playing) {
              card.resetState();
              card.state.facedown = !matchResponse.debug && player.id !== thisPlayerId;
            }
            return new PlayerState(player.id, player.name, player.seat, [...player.hand, ...player.playing]);
          }
          return player;
        }));
      }

      // Messages
      socket.on("leave", (player_name) => {
        console.log(`${player_name} has left the match`);
      });

      socket.on("join", (response) => {
        console.log(`raw join response: ${JSON.stringify(response)}`);
        const joinResponse = new JoinResponse(response);

        if (joinResponse.name === name) {
          thisPlayerId = joinResponse.id;
          setPlayerId(joinResponse.id);
        }

        // Need to use callback to ensure atomicity
        const seat = PlayerState.getSeat(joinResponse.id, matchResponse.seatOffset, matchResponse.numPlayers);
        setPlayers(prevPlayers => [...prevPlayers, new PlayerState(joinResponse.id, joinResponse.name, seat)]);
      });

      socket.on("start", (response) => {
        console.log(`raw start response: ${JSON.stringify(response)}`);
        const startResponse = new StartResponse(response);

        setGameState(new GameState(startResponse.activePlayerId, startResponse.phase));
        setTrumpState(new TrumpState(startResponse.deckSize, startResponse.gameRank));
        setBoardState(new BoardState(Array.from({length: startResponse.deckSize}, (_, i) => new Card(-(1 + i)))));
        setPlayers(prevPlayers => prevPlayers.map(player => new PlayerState(player.id, player.name, player.seat)));
      });

      socket.on("draw", (response) => {
        console.log(`raw draw response: ${JSON.stringify(response)}`);
        const drawResponse = new DrawResponse(response);

        setBoardState(pState => {
          const drawnCards = pState.deck.splice(-drawResponse.cards.length, drawResponse.cards.length);

          // Add new cards to player's hand
          setPlayers(prevPlayers => prevPlayers.map((player) => {
            if (player.id === drawResponse.id) {
              for (let i = 0; i < drawnCards.length; i++) {
                drawnCards[i].updateInfo(drawResponse.cards[i]);
              }

              return new PlayerState(player.id, player.name, player.seat, [...player.hand, ...drawnCards], player.playing);
            }
            return player;
          }));

          // Withdraw bids as game starts
          if (drawResponse.phase === GamePhase.Kitty) {
            withdrawPlaying();
          }

          return new BoardState(pState.deck, pState.kitty, pState.discard, pState.score);
        });

        // Set new game state
        setGameState(_ => new GameState(drawResponse.activePlayerId, drawResponse.phase));
      });

      socket.on("bid", (response) => {
        console.log(`raw bid response: ${JSON.stringify(response)}`);
        const bidResponse = new BidResponse(response);

        playCards(bidResponse.trumps, bidResponse.playerId);
        withdrawPlaying(bidResponse.playerId);
        setTrumpState(pState => new TrumpState(pState.numCards, pState.trumpRank, bidResponse.trumps[0].suit));
      });

      socket.on("kitty", (response) => {
        console.log(`raw kitty response: ${JSON.stringify(response)}`);
        const kittyResponse = new KittyResponse(response);
        const kittyCards = createCardDict(kittyResponse.cards);

        // Add new cards to player's hand
        setPlayers(prevPlayers => prevPlayers.map((player) => {
          if (player.id === kittyResponse.playerId) {
            const [kitty, newHand] = partition(player.hand, card => kittyCards.has(card.id));

            for (const card of kitty) {
              card.updateInfo(kittyCards.get(card.id)!);
              card.state.rotate = 0;
            }

            setBoardState(pState => new BoardState(pState.deck, kitty, pState.discard, pState.score));

            return new PlayerState(player.id, player.name, player.seat, newHand, player.playing);
          }
          return player;
        }));

        // Set new game state
        setGameState(pState => new GameState(pState.activePlayerId, kittyResponse.phase));
      });

      socket.on("play", (response) => {
        console.log(`raw play response: ${JSON.stringify(response)}`);
        const playResponse = new PlayResponse(response);

        // Play cards
        playCards(playResponse.cards, playResponse.playerId);

        // Set new game state
        setGameState(pState => new GameState(playResponse.activePlayerId, pState.phase));
      });

      socket.on("trick", async (response) => {
        console.log(`raw trick response: ${JSON.stringify(response)}`);
        const trickResponse = new TrickResponse(response);

        // Play cards
        playCards(trickResponse.play.cards, trickResponse.play.playerId);

        // Cleanup trick
        await cleanupTrickAsync(trickResponse.score);

        // Set new game state
        setGameState(pState => new GameState(trickResponse.activePlayerId, pState.phase));
      });

      socket.on("end", async (response) => {
        console.log(`raw end response: ${JSON.stringify(response)}`);
        const endResponse = new EndResponse(response);

        // Play cards
        playCards(endResponse.trick.play.cards, endResponse.trick.play.playerId);

        // Cleanup trick
        await cleanupTrickAsync(endResponse.trick.score);

        // Set new game state
        setGameState(_ => new GameState(endResponse.trick.activePlayerId, endResponse.phase));

        await new Promise(f => setTimeout(f, 1000));

        // Display kitty
        const kittyCards = createCardDict(endResponse.kitty);
        setBoardState(pState => {
          for (const card of pState.kitty) {
            card.updateInfo(kittyCards.get(card.id)!);
          }

          setPlayers(prevPlayers => {
            return prevPlayers.map((player) => {
              // Add discarded cards to playing zone
              if (player.id === endResponse.kittyId) {
                return new PlayerState(player.id, player.name, player.seat, player.hand, pState.kitty);
              }
              return player;
            });
          });

          return new BoardState([], [], pState.discard, endResponse.score);
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
      };
    }
  // Must not depend on any mutable states
  }, [socket, name, matchId, matchResponse]);

  class Controller implements ControllerInterface {
    private activeId = () => matchResponse.debug ? gameState.activePlayerId : playerId;
    private selection = () => players[this.activeId()].hand.filter(c => c.state.selected).map(c => c.toInfo());

    onSelect(selectedCard: Card) {
      setPlayers(players.map((player) => {
        const nextHand = player.hand.map((card) => {
          if (card.id === selectedCard.id && (matchResponse.debug || player.id === playerId)) {
            card.resetState();
            card.state.selected = !card.state.selected;
          }
          return card;
        });

        return new PlayerState(player.id, player.name, player.seat, nextHand, player.playing);
      }));
    }

    onNext() {
      setGameState(pState => new GameState(pState.activePlayerId, GamePhase.Waiting));
      socket?.emit("next", new NextRequest(matchId, this.activeId()));
    };

    onDraw() { socket?.emit("draw", new DrawRequest(matchId, this.activeId())); }
    onBid() { socket?.emit("bid", new BidRequest(matchId, this.activeId(), this.selection())); }
    onHide() { socket?.emit("kitty", new KittyRequest(matchId, this.activeId(), this.selection())); }
    onPlay() { socket?.emit("play", new PlayRequest(matchId, this.activeId(), this.selection())); }
  }
  const controller = new Controller();

  return (
    !socket ? (
      <p>Loading ...</p>
    ) : (
      <motion.div style={{ display: "grid", placeContent: "center", width: "100vw", height: "100vh" }}>
        <ControlZone parentZone={zone} gameState={gameState} controller={controller} />
        <CenterZone board={boardState} deckZone={deckZone} options={options} controller={controller} />
        { players.map((player) => {
          return <PlayerZone
            key={player.id}
            player={player}
            activePlayerId={gameState.activePlayerId}
            trumpState={trumpState}
            parentZone={zone}
            options={options}
            controller={controller} />
        })}
      </motion.div>
    ));
}
