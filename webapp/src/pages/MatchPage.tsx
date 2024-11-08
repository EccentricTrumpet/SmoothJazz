import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { useLocation, useParams } from "react-router-dom";
import { Manager, Socket } from "socket.io-client";
import { debounce } from "lodash";
import { Card, ControllerInterface } from "../abstractions";
import { Position, Size, Zone } from "../abstractions/bounds";
import { BoardState, CardState, GameState, OptionsState, PlayerState, TrumpState } from "../abstractions/states";
import { CardInfo, DrawRequest, GameStartResponse, JoinRequest, JoinResponse, MatchResponse, TrumpRequest, TrumpResponse } from "../abstractions/messages";
import { CenterZone, ControlZone, PlayerZone } from "../components";
import { GamePhase, Suit } from "../abstractions/enums";
import { DrawResponse } from "../abstractions/messages/DrawResponse";
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
        setTrumpState(new TrumpState(gameStartResponse.deckSize, gameStartResponse.gameRank));
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

        let drawnCards: Card[];
        setBoardState(prevBoardState => {
          drawnCards = prevBoardState.deck.slice(-drawResponse.cards.length);
          return new BoardState(
            prevBoardState.deck.slice(0, -drawResponse.cards.length),
            prevBoardState.kitty,
            prevBoardState.discard,
            prevBoardState.points
          )
        });

        // Add new cards to player's hand
        setPlayers(prevPlayers => prevPlayers.map((player) => {
          let newPlayerState: PlayerState;
          if (player.id === drawResponse.id) {
            for (let i = 0; i < drawnCards.length; i++) {
              drawnCards[i].prepareState();
              drawnCards[i].id = drawResponse.cards[i].id;
              drawnCards[i].suit = drawResponse.cards[i].suit;
              drawnCards[i].rank = drawResponse.cards[i].rank;
              drawnCards[i].state.facedown = false;
            }

            newPlayerState = new PlayerState(player.id, player.name, player.seat, [...player.hand, ...drawnCards], player.staging);
          }
          else {
            newPlayerState = player;
          }

          // Withdraw any declared trumps in preparation for game start
          if (drawResponse.phase === GamePhase.Kitty && newPlayerState.staging.length > 0) {
            for (const card of newPlayerState.staging) {
              card.prepareState();
            }
            newPlayerState.hand = [...newPlayerState.hand, ...newPlayerState.staging];
            newPlayerState.staging = [];
          }

          return newPlayerState;
        }));

        // Set new active player
        setGameState(_ => new GameState(drawResponse.activePlayerId, drawResponse.phase));
      });

      socket.on("trump", (response) => {
        console.log(`raw response: ${JSON.stringify(response)}`);
        const trumpResponse = new TrumpResponse(response);

        // Add new card to player's hand
        setPlayers(prevPlayers => prevPlayers.map((player) => {
          if (player.id === trumpResponse.playerId) {
            const [newStaging, newHand] = partition(player.hand, (card) => {
              return trumpResponse.trumps.some((trump) => trump.id === card.id);
            });

            for (const card of newStaging) {
              card.state.selected = false;
            }

            return new PlayerState(player.id, player.name, player.seat, newHand, [...player.staging, ...newStaging]);
          }
          else if (player.staging.length > 0) {
            for (const card of player.staging) {
              card.prepareState();
            }
            return new PlayerState(player.id, player.name, player.seat, [...player.hand, ...player.staging]);
          }
          else {
            return player;
          }
        }));

        setTrumpState(prevTrumpState => new TrumpState(
          prevTrumpState.numCards,
          prevTrumpState.trumpRank,
          trumpResponse.trumps[0].suit));
      });

      // Join match
      socket.emit("join", new JoinRequest(Number(matchId), name));

      return () => {
        // Teardown
        socket.emit("leave", name, matchId);
        socket.off("trump");
        socket.off("draw");
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
      const trumps: CardInfo[] = [];
      for (const card of players[playerId].hand) {
        if (card.state.selected) {
          trumps.push(new CardInfo(
            card.id,
            card.suit,
            card.rank
          ))
        }
      }
      socket?.emit("trump", new TrumpRequest(matchId, playerId, trumps));
    }

    onDrawCard = () => {
      if (matchResponse.debug || playerId === gameState.activePlayerId) {
        socket?.emit("draw", new DrawRequest(matchId, gameState.activePlayerId));
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
