import { AnimatePresence, motion } from "framer-motion";
import { debounce } from "lodash";
import { useEffect, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { Manager, Socket } from "socket.io-client";
import { Card, ControllerInterface, seatOf } from "../abstractions";
import { Position, Size, Zone } from "../abstractions/bounds";
import { GamePhase, MatchPhase } from "../abstractions/enums";
import { CardsEvent, JoinEvent, MatchResponse, PlayerEvent } from "../abstractions/messages";
import {
  BoardState, CardState, ErrorState, OptionsState, PlayerState, StatusState, TrumpState
} from "../abstractions/states";
import {
  CardsUpdate, EndUpdate, ErrorUpdate, MatchUpdate, PlayerUpdate, StartUpdate, TeamUpdate
} from "../abstractions/updates";
import { CenterZone, ControlZone, ErrorComponent, KittyZone, PlayerZone, TrumpZone } from "../components";
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

      const playCards = (cards: Card[], pid: number, winnerPid?: number) => {
        const playCards = createCardDict(cards);

        setPlayers(prevPlayers => prevPlayers.map((player) => {
          if (player.id === pid) {
            const [newPlaying, newHand] = partition(player.hand, card => playCards.has(card.id));
            newPlaying.forEach(card => card.updateInfo(playCards.get(card.id)!));
            return new PlayerState(player.id, player.name, player.level, player.seat, newHand, [...player.playing, ...newPlaying]);
          }
          return player;
        }));

        if (winnerPid !== undefined) {
          setStatusState(pState => new StatusState(pState).withWinner(winnerPid));
        }
      }

      const cleanupTrickAsync = async (score: number, activePid?: number) => {
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

        // Update status state
        setStatusState(pState => new StatusState(pState).withActivePlayer(activePid).withWinner(-1));
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
      socket.on("error", (obj) => {
        console.log(`raw error update: ${JSON.stringify(obj)}`);
        const update = new ErrorUpdate(obj);

        setError(new ErrorState(true, update.title, update.message));
        if (update.hintCards.length > 0) {
          const hintCards = createCardDict(update.hintCards);
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

      socket.on("leave", (obj) => {
        console.log(`raw leave update: ${JSON.stringify(obj)}`);
        const update = new PlayerUpdate(obj);

        if (update.pid === thisPlayerId) {
          navigate('/');
        }
        else {
          setPlayers(prevPlayers => {
            const newPlayers = prevPlayers.filter(player => player.id !== update.pid);
            const seatOffset = newPlayers.findIndex(player => player.id === thisPlayerId);
            for (let i = 0; i < newPlayers.length; i++) {
              newPlayers[i].seat = seatOf(i, seatOffset, matchResponse.numPlayers);
            }
            return newPlayers;
          });
        }
      });

      socket.on("join", (obj) => {
        console.log(`raw join update: ${JSON.stringify(obj)}`);
        const update = new PlayerUpdate(obj);

        if (update.name === name) {
          thisPlayerId = update.pid;
          setPlayerId(update.pid);
        }

        // Need to use callback to ensure atomicity
        setPlayers(prevPlayers => {
          const seatOffset = update.pid === thisPlayerId
            ? matchResponse.seatOffset
            : prevPlayers.findIndex(player => player.id === thisPlayerId);
          const seat = seatOf(prevPlayers.length, seatOffset, matchResponse.numPlayers);
          return [...prevPlayers, new PlayerState(update.pid, update.name, update.level, seat)];
        });
      });

      socket.on("team", (obj) => {
        console.log(`raw team update: ${JSON.stringify(obj)}`);
        const update = new TeamUpdate(obj);
        setStatusState(pState => new StatusState(pState).withTeamInfo(update.kittyPid, update.defenders));
      });

      socket.on("start", (obj) => {
        console.log(`raw start update: ${JSON.stringify(obj)}`);
        const update = new StartUpdate(obj);

        setStatusState(pState => new StatusState(pState)
          .withActivePlayer(update.activePid)
          .withGamePhase(GamePhase.Draw));
        setTrumpState(new TrumpState(update.cards, update.rank));
        setBoardState(new BoardState(Array.from({length: update.cards}, (_, i) => new CardState(-(1 + i)))));
        setPlayers(prevPlayers => prevPlayers.map(player => new PlayerState(player.id, player.name, player.level, player.seat)));
      });

      socket.on("match", (obj) => {
        console.log(`raw match update: ${JSON.stringify(obj)}`);
        const update = new MatchUpdate(obj);
        setStatusState(pState => new StatusState(pState).withMatchPhase(update.matchPhase));
      });

      socket.on("draw", (obj) => {
        console.log(`raw draw update: ${JSON.stringify(obj)}`);
        const update = new CardsUpdate(obj);

        setBoardState(pState => {
          const drawnCards = pState.deck.splice(-update.cards.length, update.cards.length);

          // Add new cards to player's hand
          setPlayers(prevPlayers => prevPlayers.map((player) => {
            if (player.id === update.pid) {
              for (let i = 0; i < drawnCards.length; i++) {
                drawnCards[i].updateInfo(update.cards[i]);
              }

              return new PlayerState(player.id, player.name, player.level, player.seat, [...player.hand, ...drawnCards], player.playing);
            }
            return player;
          }));

          // Withdraw bids as game starts
          if (update.phase === GamePhase.Kitty) {
            withdrawPlaying();
          }

          return new BoardState(pState.deck, pState.kitty, pState.discard, pState.score);
        });

        // Set new game state
        setStatusState(pState => new StatusState(pState)
          .withActivePlayer(update.nextPID)
          .withGamePhase(update.phase!));
      });

      socket.on("bid", (obj) => {
        console.log(`raw bid update: ${JSON.stringify(obj)}`);
        const update = new CardsUpdate(obj);

        playCards(update.cards, update.pid);
        withdrawPlaying(update.pid);
        setTrumpState(pState => new TrumpState(pState.numCards, pState.trumpRank, update.cards[0].suit));
      });

      socket.on("kitty", (obj) => {
        console.log(`raw kitty update: ${JSON.stringify(obj)}`);
        const update = new CardsUpdate(obj);
        const kittyCards = createCardDict(update.cards);

        // Add kitty cards to board state
        setPlayers(prevPlayers => prevPlayers.map((player) => {
          if (player.id === update.pid) {
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
        setStatusState(pState => new StatusState(pState).withGamePhase(update.phase!));
      });

      socket.on("play", async (obj) => {
        console.log(`raw play update: ${JSON.stringify(obj)}`);
        const update = new CardsUpdate(obj);

        // Play cards
        playCards(update.cards, update.pid, update.hintPID);

        if (update.score === undefined) {
          // Trick not complete
          setStatusState(pState => new StatusState(pState).withActivePlayer(update.nextPID));
        }
        else {
          // Trick complete
          await cleanupTrickAsync(update.score, update.nextPID);
        }
      });

      socket.on("end", async (obj) => {
        console.log(`raw end update: ${JSON.stringify(obj)}`);
        const update = new EndUpdate(obj);

        // Play cards
        playCards(update.play.cards, update.play.pid, update.play.hintPID);

        // Cleanup trick
        await cleanupTrickAsync(update.play.score!);
        await new Promise(f => setTimeout(f, 1000));

        // Display kitty
        const kittyCards = createCardDict(update.kitty.cards);
        setBoardState(pState => {
          pState.kitty.forEach(card => card.updateInfo(kittyCards.get(card.id)!));

          setPlayers(prevPlayers => {
            return prevPlayers.map(player => new PlayerState(
              player.id,
              player.name,
              update.players.get(player.id)!,
              player.seat,
              player.hand,
              player.id === update.kitty.pid ? pState.kitty : player.playing
            ));
          });

          return new BoardState([], [], pState.discard, update.kitty.score);
        });

        setStatusState(pState => new StatusState(pState)
          .withActivePlayer(update.kitty.nextPID)
          .withGamePhase(GamePhase.End));
      });

      // Join match
      socket.emit("join", new JoinEvent(Number(matchId), name));

      return () => {
        // Teardown
        socket.off("end");
        socket.off("play");
        socket.off("kitty");
        socket.off("bid");
        socket.off("draw");
        socket.off("match");
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
