import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { useLocation, useParams } from "react-router-dom";
import { Manager, Socket } from "socket.io-client";
import { debounce } from "lodash";
import { Card } from "../abstractions/Card";
import { DisplaySettings } from "../abstractions/DisplaySettings";
import { Zone } from "../abstractions/Zone";
import { Position } from "../abstractions/Position";
import { Size } from "../abstractions/Size";
import { IController } from "../abstractions/IController";
import ControlZone from "../components/ControlZone";
import PlayerZone from "../components/PlayerZone";
import { PlayerState } from "../abstractions/PlayerState";
import { SeatPosition } from "../abstractions/SeatPosition";
import CenterZone from "../components/CenterZone";
import { BoardState } from "../abstractions/BoardState";

export default function MatchPage() {
  // React states
  const { id } = useParams();
  const { state } = useLocation();

  // API states
  const [socket, setSocket] = useState<Socket>();

  // Game states
  const name = state.name;
  const [currentPlayer, setCurrentPlayer] = useState(0);

  // UI states
  const [zone, setZone] = useState(new Zone(
    new Position(0, 0),
    new Size(window.innerWidth, window.innerHeight)
  ));
  const [boardState, setBoardState] = useState(new BoardState(true));
  const [players, setPlayers] = useState([
    new PlayerState("Albert", 0, 0, SeatPosition.South, []),
    new PlayerState("Betty", 1, 1, SeatPosition.East, []),
    new PlayerState("Charlie", 2, 2, SeatPosition.North, []),
    new PlayerState("Diane", 3, 3, SeatPosition.West, []),
  ])
  const displaySettings = new DisplaySettings("red.png");

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
      // Receive messages
      socket.on("data", (data) => {
      });

      socket.on("leave", (player_name) => {
        console.log(`${player_name} has left the match`);
      });

      socket.on("join", (player_name) => {
        console.log(`${player_name} has joined the match`);
      });

      // Join match
      socket.emit("join", name, id);

      return () => {
        // Teardown
        socket.off("data");
        socket.off("join");
        socket.emit("leave", name, id);
        socket.off("leave");
      };
    }
  }, [socket, name, id]);

  class Controller implements IController {
    onDrawCard = (card: Card) => {
      const nextPlayers = players.map((player) => {
        if (player.index === currentPlayer) {
          const nextCard = new Card(
            card.id,
            card.suit,
            card.rank,
            undefined,
            card.state,
          )
          const nextHand = [...player.hand, nextCard];
          return new PlayerState(player.name, player.id, player.index, player.seatPosition, nextHand);
        }
        else {
          return player;
        }
      });

      setPlayers(nextPlayers);

      setBoardState(new BoardState(
        false,
        boardState.deck.filter(deckCard => card.id !== deckCard.id),
        boardState.kitty,
        boardState.discard,
        boardState.points
      ));

      setCurrentPlayer((currentPlayer + 1) % players.length);

      console.log(`Deck size: ${boardState.deck.length}`);
    }

    onPlayCard = (card: Card) => {
      console.log(`clicked: ${card}`);
    }
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
      <ControlZone parentZone={zone} controller={gameController} />
      <CenterZone board={boardState} parentZone={zone} settings={displaySettings} controller={gameController} />
      { players.map((player) => {
        return <PlayerZone key={player.id} player={player} parentZone={zone} settings={displaySettings} controller={gameController} />
      })}
    </motion.div>
  ));
}
