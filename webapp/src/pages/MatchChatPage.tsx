import { useEffect, useState } from "react";
import { useLocation, useParams } from "react-router-dom";
import { Manager, Socket } from "socket.io-client";

export default function MatchChatPage() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<string[]>([]);
  const [socket, setSocket] = useState<Socket>();
  const { id } = useParams();
  const { state } = useLocation();
  const name = state.name;

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
        setMessages(prevMessages => [...prevMessages, data]);
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

  // UI handlers
  const handleText = (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputMessage = e.target.value;
    setMessage(inputMessage);
  };
  const handleSubmit = () => {
    if (socket) {
      socket.emit("data", message, id);
      setMessage("");
    }
  };

  return (
    !socket ? (
      <p>Loading ...</p>
    ) : (
    <div>
      <h2>Match: {id} Player: {name}</h2>
      <input type="text" value={message} onChange={handleText} />
      <button onClick={handleSubmit}>submit</button>
      <ul>
        {messages.map((message, ind) => {
          return <li key={ind}>{message}</li>;
        })}
      </ul>
    </div>
  ));
}
