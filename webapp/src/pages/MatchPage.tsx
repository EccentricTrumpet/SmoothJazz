import { AnimatePresence, motion } from "framer-motion";
import { debounce } from "lodash";
import { useEffect, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { Manager, Socket } from "socket.io-client";
import { Card, IControl } from "../abstractions";
import { Vector, Size, Zone } from "../abstractions/bounds";
import { GamePhase, MatchPhase, Suit } from "../abstractions/enums";
import { CardsEvent, JoinEvent, MatchResponse, PlayerEvent, seatOf } from "../abstractions/messages";
import { BoardState, CardState, ErrorState, PlayerState, TrumpState } from "../abstractions/states";
import {
  CardsUpdate, EndUpdate, ErrorUpdate, MatchUpdate, PlayerUpdate, StartUpdate, TeamUpdate
} from "../abstractions/updates";
import {
  CenterZone, ControlZone, ErrorComponent, KittyZone, PlayerZone, TrumpZone
} from "../components";
import { CARD_SIZE, Styles } from "../Constants";

function partition<T>(array: T[], condition: (element: T) => boolean) : [T[], T[]] {
  return array.reduce(([pass, fail], elem) => {
    return condition(elem) ? [[...pass, elem], fail] : [pass, [...fail, elem]];
  }, [[], []] as [T[], T[]]);
}

export default function MatchPage() {
  // React states
  const navigate = useNavigate();
  const { id } = useParams();
  const matchId = Number(id);
  const { state } = useLocation();
  const [name] = useState<string>(state?.name);
  const [match] = useState<MatchResponse>(state?.matchResponse);

  // Redirect to join match if missing required match data
  useEffect(() => {
    if (!state || !name || !match) navigate(`/joinMatch?match_id=${matchId}`);
  }, [name, match, navigate, matchId, state]);

  // UI states
  const [zone, setZone] = useState(new Zone(
    Vector.Origin, new Size(window.innerWidth, window.innerHeight)
  ));
  const deck = zone.midSet(CARD_SIZE);
  const [error, setError] = useState(new ErrorState());

  // Game states
  const [PID, setPID] = useState(-1);
  const [board, setBoard] = useState(new BoardState());
  const [players, setPlayers] = useState(match?.players);
  const [socket, setSocket] = useState<Socket>();

  // Establish window size
  useEffect(() => {
    const handleResize = debounce(() => setZone(new Zone(
      Vector.Origin, new Size(window.innerWidth, window.innerHeight)
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
    if (!socket) return;
    let thisPID = -1;

    const createCardDict = (cards: Card[]) => {
      const dict = new Map<number, Card>();
      cards.forEach(card => dict.set(card.id, card));
      return dict;
    }

    const playCards = (cards: Card[], pid: number, winnerPID?: number) => {
      const playCards = createCardDict(cards);

      setPlayers(prevPlayers => prevPlayers.map(player => {
        if (player.pid !== pid) {
          return player
        }
        const [newPlaying, newHand] = partition(player.hand, card => playCards.has(card.id));
        newPlaying.forEach(card => card.update(playCards.get(card.id)!));
        return player.update({ hand: newHand, play: [...player.play, ...newPlaying] });
      }));

      if (winnerPID !== undefined) {
        setBoard(prev => prev.update({ winnerPID: winnerPID }));
      }
    }

    const cleanupTrickAsync = async (score: number, activePID?: number) => {
      await new Promise(f => setTimeout(f, 1000));

      // Remove played cards from players
      setPlayers(prevPlayers => {
        const trash: CardState[] = [];
        const newPlayers = prevPlayers.map(player => {
          for (const card of player.play) {
            card.reset();
            card.next.turn = 0;
            trash.push(card);
          }
          return player.update({ play: [] });
        });

        // Update board states
        setBoard(prev => prev.update({
          cards: prev.cards.update({trash: [...prev.cards.trash, ...trash]}),
          activePID: activePID,
          winnerPID: -1,
          score: score
        }));

        return newPlayers;
      });
    }

    const withdrawPlaying = (ignorePlayer: number | undefined = undefined) => {
      setPlayers(prevPlayers => prevPlayers.map(player => {
        if (player.pid === ignorePlayer || player.play.length === 0) {
          return player;
        }
        for (const card of player.play) {
          card.reset();
          card.next.facedown = !match.debug && player.pid !== thisPID;
        }
        return player.update({ hand: [...player.hand, ...player.play], play: [] });
      }));
    }

    // Messages
    socket.on("error", (obj) => {
      console.log(`raw error update: ${JSON.stringify(obj)}`);
      const update = new ErrorUpdate(obj);

      setError(new ErrorState(true, update.title, update.message));
      if (update.cards.length > 0) {
        const hintCards = createCardDict(update.cards);
        setPlayers(prevPlayers => prevPlayers.map(player => {
          for (const card of player.hand) {
            if (hintCards.has(card.id)) {
              card.next.focus = true;
            }
          }

          return player.update({ hand: [...player.hand] });
        }));
      }
    });

    socket.on("leave", (obj) => {
      console.log(`raw leave update: ${JSON.stringify(obj)}`);
      const update = new PlayerUpdate(obj);

      if (update.PID === thisPID) navigate('/');

      setPlayers(prevPlayers => {
        const newPlayers = prevPlayers.filter(player => player.pid !== update.PID);
        const southSeat = newPlayers.findIndex(player => player.pid === thisPID);
        for (let i = 0; i < newPlayers.length; i++) {
          newPlayers[i].seat = seatOf(i, southSeat, match.seats);
        }
        return newPlayers;
      });
    });

    socket.on("join", (obj) => {
      console.log(`raw join update: ${JSON.stringify(obj)}`);
      const update = new PlayerUpdate(obj);

      if (update.name === name && thisPID === -1) {
        thisPID = update.PID;
        setPID(update.PID);
      }

      setPlayers(prev => {
        const south = update.PID === thisPID ? prev.length : prev.findIndex(p => p.pid === thisPID);
        const seat = seatOf(prev.length, south, match.seats);
        return [...prev, new PlayerState(update.PID, update.name, update.level, seat)];
      });
    });

    socket.on("team", (obj) => {
      console.log(`raw team update: ${JSON.stringify(obj)}`);
      const update = new TeamUpdate(obj);
      setBoard(prev => prev.update({ kittyPID: update.kittyPID, defenders: update.defenders }));
    });

    socket.on("start", (obj) => {
      console.log(`raw start update: ${JSON.stringify(obj)}`);
      const update = new StartUpdate(obj);

      setBoard(prev => {
        const deck = Array.from({length: update.cards}, (_, i) => new CardState(prev.options, -1-i));

        return prev.update({
          cards: prev.cards.update({deck: deck, kitty: [], trash: []}),
          trump: new TrumpState(update.cards, update.rank, Suit.Joker),
          activePID: update.activePID,
          game: GamePhase.Draw
      })});
      setPlayers(prevPlayers => prevPlayers.map(player => player.update({ play: [] })));
    });

    socket.on("match", (obj) => {
      console.log(`raw match update: ${JSON.stringify(obj)}`);
      const update = new MatchUpdate(obj);
      setBoard(prev => prev.update({match: update.phase}));
    });

    socket.on("draw", (obj) => {
      console.log(`raw draw update: ${JSON.stringify(obj)}`);
      const update = new CardsUpdate(obj);

      setBoard(prev => {
        const drawnCards = prev.cards.deck.splice(-update.cards.length, update.cards.length);

        // Add new cards to player's hand
        setPlayers(prevPlayers => prevPlayers.map((player) => {
          if (player.pid === update.pid) {
            for (let i = 0; i < drawnCards.length; i++) {
              drawnCards[i].update(update.cards[i]);
            }

            return player.update({ hand: [...player.hand, ...drawnCards] });
          }
          return player;
        }));

        // Withdraw bids as game starts
        if (update.phase === GamePhase.Kitty) withdrawPlaying();
        return prev.update({ activePID: update.nextPID, game: update.phase });
      });
    });

    socket.on("bid", (obj) => {
      console.log(`raw bid update: ${JSON.stringify(obj)}`);
      const update = new CardsUpdate(obj);

      playCards(update.cards, update.pid);
      withdrawPlaying(update.pid);
      setBoard(prev => prev.update({ trump: prev.trump.update(update.cards[0].suit) }));
    });

    socket.on("kitty", (obj) => {
      console.log(`raw kitty update: ${JSON.stringify(obj)}`);
      const update = new CardsUpdate(obj);
      const kittyCards = createCardDict(update.cards);

      // Add kitty cards to board state
      setPlayers(prevPlayers => prevPlayers.map(player => {
        if (player.pid === update.pid) {
          const [kitty, newHand] = partition(player.hand, card => kittyCards.has(card.id));

          for (const card of kitty) {
            card.update(kittyCards.get(card.id)!);
            card.next.turn = 0;
          }

          setBoard(prev => prev.update({
            cards: prev.cards.update({kitty: kitty}), game: update.phase,
          }));

          return player.update({ hand: newHand });
        }
        return player;
      }));
    });

    socket.on("play", async (obj) => {
      console.log(`raw play update: ${JSON.stringify(obj)}`);
      const update = new CardsUpdate(obj);

      // Play cards
      playCards(update.cards, update.pid, update.hintPID);

      if (update.score === undefined) {
        // Trick not complete
        setBoard(prev => prev.update({activePID: update.nextPID}));
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
      setBoard(prev => {
        prev.cards.kitty.forEach(card => card.update(kittyCards.get(card.id)!));

        setPlayers(prevPlayers => prevPlayers.map(player => player.update({
          level: update.levels.get(player.pid),
          play: player.pid === update.kitty.pid ? prev.cards.kitty : player.play
        })));

        return prev.update({
          cards: prev.cards.update({ kitty: [] }),
          activePID: update.kitty.nextPID,
          game: GamePhase.End,
          score: update.kitty.score
        });
      });
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
  // Must not depend on any mutable states
  }, [socket, name, matchId, match, navigate]);

  class Control implements IControl {
    private pid = () => match.debug ? board.activePID : PID;
    private picked = () => players.find(p => p.pid === this.pid())!.hand
      .filter(c => c.next.picked).map(c => c.card());

    pick(picked: CardState) {
      setPlayers(players.map(player => player.update({ hand: player.hand.map(card => {
        if (card.id === picked.id && (match.debug || player.pid === PID)) {
          card.reset();
          card.next.picked = !card.next.picked;
        }
        return card;
      })})));
    }

    next() {
      setBoard(prev => prev.update({game: GamePhase.Waiting}));
      socket?.emit("next", new PlayerEvent(matchId, this.pid()));
    };

    leave() { socket?.emit("leave", new PlayerEvent(matchId, this.pid())); };
    draw() { socket?.emit("draw", new PlayerEvent(matchId, this.pid())); }
    bid() { socket?.emit("bid", new CardsEvent(matchId, this.pid(), this.picked())); }
    hide() { socket?.emit("kitty", new CardsEvent(matchId, this.pid(), this.picked())); }
    play() {
      // Reset highlights
      setPlayers(prevPlayers => prevPlayers.map(player => {
        player.hand.forEach(card => card.next.focus = false);
        return player.update();
      }));

      socket?.emit("play", new CardsEvent(matchId, this.pid(), this.picked()));
    }
  }
  const control = new Control();

  return (!socket ?
    <p>Loading ...</p> :
    <motion.div style={Styles.window}>
      { players.map(p =>
        <PlayerZone key={p.pid} player={p} board={board} parent={zone} control={control} />)
      }
      { board.matchPhase === MatchPhase.Started && <TrumpZone parent={zone} trump={board.trump} /> }
      <ControlZone parent={zone} board={board} control={control} />
      <CenterZone board={board} deck={deck} control={control} />
      <KittyZone board={board} deck={deck} />
      <AnimatePresence initial={false} mode="wait" onExitComplete={ () => null } >
      { error.show && <ErrorComponent error={error} onClose={() => setError(new ErrorState())} /> }
      </AnimatePresence>
    </motion.div>
  );
}
