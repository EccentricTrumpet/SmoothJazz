import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { Manager, Socket } from "socket.io-client";
import { debounce } from "lodash";
import { Card, ControllerInterface, seatOf } from "../abstractions";
import { Position, Size, Zone } from "../abstractions/bounds";
import { GamePhase, MatchPhase } from "../abstractions/enums";
import {
  PlayerEvent,
  DrawResponse,
  StartResponse,
  JoinEvent,
  PlayerUpdate,
  MatchResponse,
  CardsEvent,
  BidResponse,
  KittyResponse,
  PlayResponse,
  TrickResponse,
  EndResponse,
  ErrorUpdate,
  MatchUpdate} from "../abstractions/messages";
import { ErrorState, BoardState, CardState, StatusState, OptionsState, PlayerState, TrumpState } from "../abstractions/states";
import { ErrorComponent, CenterZone, ControlZone, KittyZone, PlayerZone, TrumpZone } from "../components";
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
  const navigate = useNavigate();
  const matchId = Number(id);
  const [name] = useState<string>(state?.name);
  const [matchResponse] = useState<MatchResponse>(state?.matchResponse);

  // Redirect to join match if missing required match data
  useEffect(() => {
    if (!state || !name || !matchResponse) {
      navigate(`/joinMatch?match_id=${matchId}`);
    }
  }, [name, matchResponse, navigate, matchId, state]);

  // UI states
  const options = new OptionsState("red.png");
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
  const [error, setError] = useState(new ErrorState());

  // Game states
  const [playerId, setPlayerId] = useState(-1);
  const [statusState, setStatusState] = useState(new StatusState());
  const [boardState, setBoardState] = useState(new BoardState());
  const [trumpState, setTrumpState] = useState(new TrumpState(0, 0));
  const [players, setPlayers] = useState(matchResponse?.players);
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

  // Prompt before leaving page
  useEffect(() => {
    const handleBeforeUnload = (event: BeforeUnloadEvent) => event.preventDefault();
    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
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

      const createCardDict = (cards: Card[]) => {
        const dict = new Map<number, Card>();
        cards.forEach(card => dict.set(card.id, card));
        return dict;
      }

      const playCards = (cards: Card[], playerId: number) => {
        const playCards = createCardDict(cards);

        setPlayers(prevPlayers => prevPlayers.map((player) => {
          if (player.id === playerId) {
            const [newPlaying, newHand] = partition(player.hand, card => playCards.has(card.id));
            newPlaying.forEach(card => card.updateInfo(playCards.get(card.id)!));
            return new PlayerState(player.id, player.name, player.level, player.seat, newHand, [...player.playing, ...newPlaying]);
          }
          return player;
        }));
      }

      const cleanupTrickAsync = async (score: number) => {
        await new Promise(f => setTimeout(f, 1000));

        // Remove played cards from players
        setPlayers(prevPlayers => {
          const discards: CardState[] = [];
          const newPlayers = prevPlayers.map((player) => {
            for (const card of player.playing) {
              card.resetState();
              card.state.rotate = 0;
              discards.push(card);
            }
            return new PlayerState(player.id, player.name, player.level, player.seat, player.hand);
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
            return new PlayerState(player.id, player.name, player.level, player.seat, [...player.hand, ...player.playing]);
          }
          return player;
        }));
      }

      // Messages
      socket.on("error", (response) => {
        console.log(`raw error response: ${JSON.stringify(response)}`);
        const errorResponse = new ErrorUpdate(response);

        setError(new ErrorState(true, errorResponse.title, errorResponse.message));
        if (errorResponse.hintCards.length > 0) {
          const hintCards = createCardDict(errorResponse.hintCards);
          setPlayers(prevPlayers => prevPlayers.map((player) => {
            for (const card of player.hand) {
              if (hintCards.has(card.id)) {
                card.state.highlighted = true;
              }
            }

            return new PlayerState(player.id, player.name, player.level, player.seat, [...player.hand], player.playing);
          }));
        }
      });

      socket.on("leave", (response) => {
        console.log(`raw leave response: ${JSON.stringify(response)}`);
        const update = new PlayerUpdate(response);

        if (update.id === thisPlayerId) {
          navigate('/');
        }
        else {
          setPlayers(prevPlayers => {
            const newPlayers = prevPlayers.filter(player => player.id !== update.id);
            const seatOffset = newPlayers.findIndex(player => player.id === thisPlayerId);
            for (let i = 0; i < newPlayers.length; i++) {
              newPlayers[i].seat = seatOf(i, seatOffset, matchResponse.numPlayers);
            }
            return newPlayers;
          });
        }
      });

      socket.on("join", (response) => {
        console.log(`raw join response: ${JSON.stringify(response)}`);
        const update = new PlayerUpdate(response);

        if (update.name === name) {
          thisPlayerId = update.id;
          setPlayerId(update.id);
        }

        // Need to use callback to ensure atomicity
        setPlayers(prevPlayers => {
          const seatOffset = update.id === thisPlayerId
            ? matchResponse.seatOffset
            : prevPlayers.findIndex(player => player.id === thisPlayerId);
          const seat = seatOf(prevPlayers.length, seatOffset, matchResponse.numPlayers);
          return [...prevPlayers, new PlayerState(update.id, update.name, update.level, seat)];
        });
      });

      socket.on("start", (response) => {
        console.log(`raw start response: ${JSON.stringify(response)}`);
        const startResponse = new StartResponse(response);

        setStatusState(pState => new StatusState(pState)
          .withActivePlayer(startResponse.activePlayerId)
          .withGamePhase(startResponse.phase)
          .withTeamInfo(startResponse.kittyPlayerId, startResponse.attackers, startResponse.defenders));
        setTrumpState(new TrumpState(startResponse.deckSize, startResponse.gameRank));
        setBoardState(new BoardState(Array.from({length: startResponse.deckSize}, (_, i) => new CardState(-(1 + i)))));
        setPlayers(prevPlayers => prevPlayers.map(player => new PlayerState(player.id, player.name, player.level, player.seat)));
      });

      socket.on("phase", (response) => {
        console.log(`raw phase response: ${JSON.stringify(response)}`);
        const phaseResponse = new MatchUpdate(response);

        setStatusState(pState => new StatusState(pState).withMatchPhase(phaseResponse.matchPhase));
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

              return new PlayerState(player.id, player.name, player.level, player.seat, [...player.hand, ...drawnCards], player.playing);
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
        setStatusState(pState => new StatusState(pState)
          .withActivePlayer(drawResponse.activePlayerId)
          .withGamePhase(drawResponse.phase));
      });

      socket.on("bid", (response) => {
        console.log(`raw bid response: ${JSON.stringify(response)}`);
        const bidResponse = new BidResponse(response);

        playCards(bidResponse.trumps, bidResponse.playerId);
        withdrawPlaying(bidResponse.playerId);
        setTrumpState(pState => new TrumpState(pState.numCards, pState.trumpRank, bidResponse.trumps[0].suit));
        setStatusState(pState => new StatusState(pState)
          .withTeamInfo(bidResponse.kittyPlayerId, bidResponse.attackers, bidResponse.defenders));
      });

      socket.on("kitty", (response) => {
        console.log(`raw kitty response: ${JSON.stringify(response)}`);
        const kittyResponse = new KittyResponse(response);
        const kittyCards = createCardDict(kittyResponse.cards);

        // Add kitty cards to board state
        setPlayers(prevPlayers => prevPlayers.map((player) => {
          if (player.id === kittyResponse.playerId) {
            const [kitty, newHand] = partition(player.hand, card => kittyCards.has(card.id));

            for (const card of kitty) {
              card.updateInfo(kittyCards.get(card.id)!);
              card.state.rotate = 0;
            }

            setBoardState(pState => new BoardState(pState.deck, kitty, pState.discard, pState.score));

            return new PlayerState(player.id, player.name, player.level, player.seat, newHand, player.playing);
          }
          return player;
        }));

        // Set new game state
        setStatusState(pState => new StatusState(pState).withGamePhase(kittyResponse.phase));
      });

      socket.on("play", (response) => {
        console.log(`raw play response: ${JSON.stringify(response)}`);
        const playResponse = new PlayResponse(response);

        // Play cards
        playCards(playResponse.cards, playResponse.playerId);

        // Set new game state
        setStatusState(pState => new StatusState(pState)
          .withActivePlayer(playResponse.activePlayerId)
          .withTrickWinner(playResponse.trickWinnerId));
      });

      socket.on("trick", async (response) => {
        console.log(`raw trick response: ${JSON.stringify(response)}`);
        const trickResponse = new TrickResponse(response);

        // Play cards
        playCards(trickResponse.play.cards, trickResponse.play.playerId);

        // Set status state
        setStatusState(pState => new StatusState(pState).withTrickWinner(trickResponse.activePlayerId));

        // Cleanup trick
        await cleanupTrickAsync(trickResponse.score);

        // Set status state
        setStatusState(pState => new StatusState(pState)
          .withActivePlayer(trickResponse.activePlayerId)
          .withTrickWinner(-1));
      });

      socket.on("end", async (response) => {
        console.log(`raw end response: ${JSON.stringify(response)}`);
        const endResponse = new EndResponse(response);

        // Play cards
        playCards(endResponse.trick.play.cards, endResponse.trick.play.playerId);

        // Set status state
        setStatusState(pState => new StatusState(pState)
          .withTrickWinner(endResponse.trick.activePlayerId));

        // Cleanup trick
        await cleanupTrickAsync(endResponse.trick.score);

        // Set new game state
        setStatusState(pState => new StatusState(pState)
          .withActivePlayer(endResponse.trick.activePlayerId)
          .withTrickWinner(-1));

        await new Promise(f => setTimeout(f, 1000));

        // Display kitty
        const kittyCards = createCardDict(endResponse.kitty);
        setBoardState(pState => {
          for (const card of pState.kitty) {
            card.updateInfo(kittyCards.get(card.id)!);
          }

          setPlayers(prevPlayers => {
            return prevPlayers.map(player => new PlayerState(
              player.id,
              player.name,
              endResponse.players.get(player.id)!,
              player.seat,
              player.hand,
              player.id === endResponse.kittyId ? pState.kitty : player.playing
            ));
          });

          return new BoardState([], [], pState.discard, endResponse.score);
        });

        setStatusState(pState => new StatusState(pState)
          .withActivePlayer(endResponse.leadId)
          .withGamePhase(endResponse.phase));
      });

      // Join match
      socket.emit("join", new JoinEvent(Number(matchId), name));

      return () => {
        // Teardown
        socket.off("end");
        socket.off("trick");
        socket.off("play");
        socket.off("kitty");
        socket.off("bid");
        socket.off("draw");
        socket.off("phase");
        socket.off("start");
        socket.off("join");
        socket.off("leave");
        socket.off("error");
      };
    }
  // Must not depend on any mutable states
  }, [socket, name, matchId, matchResponse, navigate]);

  class Controller implements ControllerInterface {
    private activeId = () => matchResponse.debug ? statusState.activePlayerId : playerId;
    private selection = () => players.find(player => player.id === this.activeId())!.hand
      .filter(c => c.state.selected).map(c => c.toInfo());

    onSelect(selectedCard: CardState) {
      setPlayers(players.map((player) => {
        const nextHand = player.hand.map((card) => {
          if (card.id === selectedCard.id && (matchResponse.debug || player.id === playerId)) {
            card.resetState();
            card.state.selected = !card.state.selected;
          }
          return card;
        });

        return new PlayerState(player.id, player.name, player.level, player.seat, nextHand, player.playing);
      }));
    }

    onNext() {
      setStatusState(pState => new StatusState(pState).withGamePhase(GamePhase.Waiting));
      socket?.emit("next", new PlayerEvent(matchId, this.activeId()));
    };

    onLeave() { socket?.emit("leave", new PlayerEvent(matchId, this.activeId())); };
    onDraw() { socket?.emit("draw", new PlayerEvent(matchId, this.activeId())); }
    onBid() { socket?.emit("bid", new CardsEvent(matchId, this.activeId(), this.selection())); }
    onHide() { socket?.emit("kitty", new CardsEvent(matchId, this.activeId(), this.selection())); }
    onPlay() {
      // Reset highlights
      setPlayers(prevPlayers => prevPlayers.map((player) => {
        player.hand.forEach(card => card.state.highlighted = false);
        return new PlayerState(player.id, player.name, player.level, player.seat, [...player.hand], player.playing);
      }));

      socket?.emit("play", new CardsEvent(matchId, this.activeId(), this.selection()));
    }
  }
  const controller = new Controller();

  return (
    !socket ? (
      <p>Loading ...</p>
    ) : (
      <motion.div style={{ display: "grid", placeContent: "center", width: "100vw", height: "100vh" }}>
        { players.map((player) => {
          return <PlayerZone
            key={player.id}
            player={player}
            trumpState={trumpState}
            statusState={statusState}
            parentZone={zone}
            options={options}
            controller={controller} />
        })}
        {statusState.matchPhase === MatchPhase.STARTED && <TrumpZone parentZone={zone} trumpState={trumpState} />}
        <ControlZone parentZone={zone} statusState={statusState} controller={controller} />
        <CenterZone board={boardState} deckZone={deckZone} options={options} controller={controller} />
        <KittyZone board={boardState} deckZone={deckZone} trumpState={trumpState} options={options} />
        <AnimatePresence
          initial={false}
          mode="wait"
          onExitComplete={() => null}
        >
          {error.show && <ErrorComponent errorState={error} onClose={() => setError(new ErrorState())}/>}
        </AnimatePresence>
      </motion.div>
    ));
}
