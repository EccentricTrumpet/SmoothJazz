import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { useLocation, useParams } from "react-router-dom";
import { Manager, Socket } from "socket.io-client";
import { debounce } from "lodash";
import { Card, ControllerInterface } from "../abstractions";
import { Position, Size, Zone } from "../abstractions/bounds";
import { BoardState, CardState, GameState, OptionsState, PlayerState, TrumpState } from "../abstractions/states";
import { DrawRequest, GameStartResponse, JoinRequest, JoinResponse, MatchResponse } from "../abstractions/messages";
import { CenterZone, ControlZone, PlayerZone } from "../components";
import { Suit } from "../abstractions/enums";
import { DrawResponse } from "../abstractions/messages/DrawResponse";
import { Constants } from "../Constants";

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
      // Receive messages
      socket.on("data", (data) => {
      });

      socket.on("leave", (player_name) => {
        console.log(`${player_name} has left the match`);
      });

      socket.on("join", (response) => {
        const joinResponse = new JoinResponse(response);

        if (joinResponse.name === name) {
          setPlayerId(joinResponse.id);
        }

        // Need to use callback to ensure atomicity
        setPlayers(prevPlayers => [...prevPlayers, new PlayerState(
          joinResponse.id,
          joinResponse.name,
          PlayerState.getSeat(joinResponse.id, matchResponse.seatOffset, matchResponse.numPlayers)
        )]);
      });

      socket.on("gameStart", (response) => {
        const gameStartResponse = new GameStartResponse(response);

        setGameState(new GameState(gameStartResponse.activePlayerId, gameStartResponse.gamePhase));
        setTrumpState(new TrumpState(gameStartResponse.deckSize, gameStartResponse.trumpRank));
        setBoardState(new BoardState(
          Array(gameStartResponse.deckSize).fill('').map((_, i) =>
            new Card(-(1 + i), Suit.Unknown, 0, new CardState(
              true,
              false,
              0,
              new Position(0, 0),
              new Position(i/3, 0)
            ))
          )
        ));
      });

      socket.on("draw", (response) => {
        const drawResponse = new DrawResponse(response);

        for (const card of drawResponse.cards) {
          // Remove card from deck
          let topCard: Card;
          setBoardState(prevBoardState => {
            topCard = prevBoardState.deck[prevBoardState.deck.length - 1];
            return new BoardState(
              prevBoardState.deck.slice(0, -1),
              prevBoardState.kitty,
              prevBoardState.discard,
              prevBoardState.points
            )
          });

          // Add new card to player's hand
          setPlayers(prevPlayers => prevPlayers.map((player) => {
            if (player.id === drawResponse.id) {
              const newCard = topCard.clone();
              newCard.id = card.id;
              newCard.suit = card.suit;
              newCard.rank = card.rank;
              newCard.state.facedown = false;

              return new PlayerState(player.id, player.name, player.seat, [...player.hand, newCard]);
            }
            else {
              return player;
            }
          }));
        }

        // Set new active player
        setGameState(_prevGameState => {
          return new GameState(drawResponse.activePlayerId, drawResponse.phase);
        })
      });

      // Join match
      socket.emit("join", new JoinRequest(Number(matchId), name));

      return () => {
        // Teardown
        socket.emit("leave", name, matchId);
        socket.off("gameStart");
        socket.off("join");
        socket.off("leave");
        socket.off("data");
      };
    }
  // Must not depend on any mutable states
  }, [socket, name, matchId, matchResponse]);

  class Controller implements ControllerInterface {
    onDeclare = (playerId: number) => {

    }

    onDrawCard = (card: Card) => {
      if (matchResponse.debug || playerId === gameState.activePlayerId) {
        socket?.emit("draw", new DrawRequest(matchId, gameState.activePlayerId))
      }
    }

    onSelectCard = (selectedCard: Card) => {
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

        return updated ? new PlayerState(player.id, player.name, player.seat, nextHand) : player;
      });
      setPlayers(nextPlayers);
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
      <ControlZone parentZone={zone} gameState={gameState} playerId={playerId} controller={gameController} debug={matchResponse.debug} />
      <CenterZone board={boardState} deckZone={deckZone} options={options} controller={gameController} />
      { players.map((player) => {
        return <PlayerZone key={player.id} player={player} trumpState={trumpState} parentZone={zone} options={options} controller={gameController} />
      })}
    </motion.div>
  ));
}
