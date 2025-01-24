import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { Manager, Socket } from "socket.io-client";
import { Card, IControl } from "../abstractions";
import { Size, Vector, Zone } from "../abstractions/bounds";
import { GamePhase, MatchPhase, Suit } from "../abstractions/enums";
import { CardsEvent, JoinEvent, MatchResponse, PlayerEvent, seatOf } from "../abstractions/messages";
import { BoardState, CardState, ErrorState, PlayerState, TrumpState } from "../abstractions/states";
import {
  CardsUpdate, EndUpdate, ErrorUpdate, MatchUpdate, PlayerUpdate, StartUpdate, TeamUpdate
} from "../abstractions/updates";
import { CenterZone, ControlZone, Error, KittyZone, LogsZone, PlayerZone, TrumpZone } from "../components";
import { CARD_SIZE, Styles } from "../Constants";

function partition<T>(a: T[], cond: (e: T) => boolean) : [T[], T[]] {
  return a.reduce(([t, f], e) => cond(e) ? [[...t, e], f] : [t, [...f, e]], [[], []] as [T[], T[]]);
}

export default function MatchPage() {
  // React states
  const navigate = useNavigate();
  const { id } = useParams();
  const matchId = Number(id);
  const { state } = useLocation();
  const [name] = useState<string>(state?.name);
  const match = useMemo(() => new MatchResponse(state?.match), [state]);

  // Redirect to join match if missing required match data
  useEffect(() => {
    if (!state || !name)
      navigate(`/joinMatch?match_id=${matchId}`);
  }, [name, navigate, matchId, state]);

  // UI states
  const [zone, setZone] = useState(new Zone(
    Vector.Origin, new Size(window.innerWidth, window.innerHeight)
  ));
  const deck = zone.midSet(CARD_SIZE);

  // Game states
  const [error, setError] = useState(new ErrorState());
  const [PID, setPID] = useState(-1);
  const [board, setBoard] = useState(new BoardState());
  const [logs, setLogs] = useState([] as string[]);
  const [players, setPlayers] = useState(match?.players);
  const [socket, setSocket] = useState<Socket>();

  // Establish window size
  useEffect(() => {
    const resize = () =>
      setZone(new Zone(Vector.Origin, new Size(window.innerWidth, window.innerHeight)));
    window.addEventListener("resize", resize);
    return () => window.removeEventListener("resize", resize);
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

    matchSocket.on("disconnect", () => console.log('socket disconnected'));
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
    if (!socket)
      return;
    let thisPID = -1;

    const toCardDict = (cards: Card[]) =>
      cards.reduce((dict, card) => dict.set(card.id, card), new Map<number, Card>());

    const playCards = (update: CardsUpdate, message = "played") => {
      const dict = toCardDict(update.cards);
      const trickCompleted = update.score !== undefined;

      setPlayers(prev => {
        let winnerName = "";
        const players = prev.map(player => {
          if (trickCompleted && player.pid === update.nextPID)
            winnerName = player.name;
          if (player.pid !== update.pid)
            return player;

          const name = prev.find(player => player.pid === update.pid)?.name;
          addLog(`${name} ${message} ${update.cards.map(c => c.toString()).join(", ")}`);
          const [play, hand] = partition(player.hand, card => dict.has(card.id));
          play.forEach(card => card.update(dict.get(card.id)));
          return player.update({ hand: hand, play: [...player.play, ...play] });
        });

        setBoard(prev => {
          if (update.score !== undefined)
            addLog(`${winnerName} won the trick ${update.score! > prev.score
              ? ` and scored ${update.score! - prev.score} points` : ""}`);
          return prev.update({ winnerPID: update.hintPID })
        });

        return players;
      });
    }

    const cleanupTrickAsync = async (score?: number, activePID?: number) => {
      await new Promise(f => setTimeout(f, 1000));

      // Remove played cards from players
      setPlayers(prev => {
        const trash: CardState[] = [];
        const players = prev.map(player => {
          player.play.forEach(card => trash.push(card.reset({ turn: 0 })))
          return player.update({ play: [] });
        });

        // Update board states
        setBoard(prev => prev.update({
          trash: [...prev.trash, ...trash], activePID: activePID, winnerPID: -1, score: score
        }));

        return players;
      });
    }

    const withdrawPlaying = (ignorePlayer: number | undefined = undefined) => {
      setPlayers(prevPlayers => prevPlayers.map(player => {
        if (player.pid === ignorePlayer || player.play.length === 0)
          return player;

        player.play.forEach(card =>
          card.reset({ suit:
            (!match.settings.debug && player.pid !== thisPID) ? Suit.Unknown : card.suit
          }));

        return player.update({ hand: [...player.hand, ...player.play], play: [] });
      }));
    }

    const addLog = (log: string) => setLogs(p => [...p, log].slice(Math.max(p.length - 5, 0)));

    // Messages
    socket.on("error", (obj) => {
      console.log(`raw error update: ${JSON.stringify(obj)}`);
      const update = new ErrorUpdate(obj);
      setError(new ErrorState(true, update.title, update.message));
      setPlayers(prev => prev.map(player => player.updateFocus(toCardDict(update.cards))));
    });

    socket.on("leave", (obj) => {
      console.log(`raw leave update: ${JSON.stringify(obj)}`);
      const update = new PlayerUpdate(obj);
      addLog(`${update.name} has left the match`);

      if (update.PID === thisPID)
        navigate('/');

      setPlayers(prev => {
        const newPlayers = prev.filter(player => player.pid !== update.PID);
        const southSeat = newPlayers.findIndex(player => player.pid === thisPID);
        for (let i = 0; i < newPlayers.length; i++)
          newPlayers[i].seat = seatOf(i, southSeat, match.settings.seats);
        return newPlayers;
      });
    });

    socket.on("join", (obj) => {
      console.log(`raw join update: ${JSON.stringify(obj)}`);
      const update = new PlayerUpdate(obj);
      addLog(`${update.name} has joined the match`);

      if (update.name === name && thisPID === -1) {
        thisPID = update.PID;
        setPID(update.PID);
      }

      setPlayers(prev => {
        const south = update.PID === thisPID ? prev.length : prev.findIndex(p => p.pid === thisPID);
        const seat = seatOf(prev.length, south, match.settings.seats);
        return [...prev, new PlayerState(update.PID, update.name, update.level, seat)];
      });
    });

    socket.on("team", (obj) => {
      console.log(`raw team update: ${JSON.stringify(obj)}`);
      const update = new TeamUpdate(obj);
      setBoard(prev => {
        return prev.update({ kittyPID: update.kittyPID, defenders: update.defenders });
      });
    });

    socket.on("start", (obj) => {
      console.log(`raw start update: ${JSON.stringify(obj)}`);
      const update = new StartUpdate(obj);
      addLog(`Level ${update.rank} game started`);

      setPlayers(prev => prev.map(player => player.update({ play: [] })));
      setBoard(prev => prev.update({
          deck: Array.from({length: update.cards}, (_, i) => new CardState(prev.options, -1-i)),
          trash: [],
          trump: new TrumpState(update.cards, update.rank, Suit.Joker),
          activePID: update.activePID,
          game: GamePhase.Draw
      }));
    });

    socket.on("match", (obj) => {
      console.log(`raw match update: ${JSON.stringify(obj)}`);
      const update = new MatchUpdate(obj);
      addLog(`Match ${MatchPhase[update.phase].toLowerCase()}`);
      setBoard(prev => prev.update({match: update.phase}));
    });

    socket.on("draw", (obj) => {
      console.log(`raw draw update: ${JSON.stringify(obj)}`);
      const update = new CardsUpdate(obj);

      setBoard(prev => {
        const draw = prev.deck.splice(-update.cards.length, update.cards.length);
        draw.forEach((card, i) => card.update(update.cards[i]));

        // Add new cards to player's hand
        setPlayers(prev => prev.map(player =>
          player.update(player.pid === update.pid ? { hand: [...player.hand, ...draw] } : undefined)
        ));

        // Withdraw bids as game starts
        if (update.phase === GamePhase.Kitty)
          withdrawPlaying();

        return prev.update({ activePID: update.nextPID, game: update.phase });
      });
    });

    socket.on("bid", (obj) => {
      console.log(`raw bid update: ${JSON.stringify(obj)}`);
      const update = new CardsUpdate(obj);

      playCards(update, "made a bid of");
      withdrawPlaying(update.pid);
      setBoard(prev => {
        return prev.update({ trump: prev.trump.update(update.cards[0].suit) })
      });
    });

    socket.on("kitty", (obj) => {
      console.log(`raw kitty update: ${JSON.stringify(obj)}`);
      const update = new CardsUpdate(obj);
      const kittyCards = toCardDict(update.cards);

      // Add kitty cards to board state
      setPlayers(prev => prev.map(player => {
        if (player.pid !== update.pid)
          return player;

        const [kitty, hand] = partition(player.hand, card => kittyCards.has(card.id));
        kitty.forEach(card => card.update(kittyCards.get(card.id), 0));
        setBoard(prev => prev.update({ kitty: kitty, game: update.phase }));
        return player.update({ hand: hand });
      }));
    });

    socket.on("play", async (obj) => {
      console.log(`raw play update: ${JSON.stringify(obj)}`);
      const update = new CardsUpdate(obj);

      // Play cards
      playCards(update);

      // Update states according to trick completion
      if (update.score === undefined) {
        setBoard(prev => prev.update({activePID: update.nextPID}));
      } else {
        await cleanupTrickAsync(update.score, update.nextPID);
      }
    });

    socket.on("end", async (obj) => {
      console.log(`raw end update: ${JSON.stringify(obj)}`);
      const update = new EndUpdate(obj);

      // Play cards
      playCards(update.play);

      // Cleanup trick
      await cleanupTrickAsync(update.play.score);
      await new Promise(f => setTimeout(f, 1000));

      // Display kitty
      const kittyCards = toCardDict(update.kitty.cards);
      setBoard(prev => {
        prev.kitty.forEach(card => card.update(kittyCards.get(card.id)));

        setPlayers(prevPlayers => prevPlayers.map(player => {
          if (player.pid === update.kitty.pid) {
            const name = prevPlayers.find(player => player.pid === update.kitty.pid)?.name;
            addLog(`${name}'s kitty was ${update.kitty.cards.map(c => c.toString()).join(", ")}`);
            addLog(`${prev.defenders.includes(update.kitty.nextPID!) ? "Defenders" : "Attackers"}
              won with a final score of ${update.kitty.score}`);
          }
          return player.update({
            level: update.levels.get(player.pid),
            play: player.pid === update.kitty.pid ? prev.kitty : player.play
          })
        }));

        return prev.update({
          kitty: [], activePID: update.kitty.nextPID, game: GamePhase.End, score: update.kitty.score
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
    private pid = () => match.settings.debug ? board.activePID : PID;
    private picked = () => players.find(p => p.pid === this.pid())?.hand
      ?.filter(c => c.next.picked)?.map(c => c.card()) ?? [];

    bid = () => socket?.emit("bid", new CardsEvent(matchId, this.pid(), this.picked()));
    draw = () => socket?.emit("draw", new PlayerEvent(matchId, this.pid()));
    hide = () => socket?.emit("kitty", new CardsEvent(matchId, this.pid(), this.picked()));
    leave = () => socket?.emit("leave", new PlayerEvent(matchId, this.pid()));
    next = () => {
      setBoard(prev => prev.update({game: GamePhase.Waiting}));
      socket?.emit("next", new PlayerEvent(matchId, this.pid()));
    };
    pick = (picked: CardState) => setPlayers(players.map(player => player.update({
      hand: player.hand.map(card => card.reset({ picked:
        (card.id === picked.id && (match.settings.debug || player.pid === PID)) !== card.next.picked
      })
    )})));
    play = () => {
      // Reset highlights
      setPlayers(prev => prev.map(player => player.updateFocus()));
      socket?.emit("play", new CardsEvent(matchId, this.pid(), this.picked()));
    };
  }
  board.control = new Control();

  return (!socket ?
    <p>Loading ...</p> :
    <motion.div style={Styles.window}>
      { players.map(p => <PlayerZone key={p.pid} player={p} board={board} parent={zone} />) }
      { board.match === MatchPhase.Started && <TrumpZone parent={zone} trump={board.trump} /> }
      <ControlZone parent={zone} board={board} />
      <CenterZone board={board} deck={deck} />
      <KittyZone board={board} deck={deck} />
      { match.settings.logs && <LogsZone logs={logs} deck={deck} /> }
      <AnimatePresence initial={false} mode="wait">
        { error.show && <Error error={error} onClose={() => setError(new ErrorState())} /> }
      </AnimatePresence>
    </motion.div>
  );
}
