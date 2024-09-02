import { BrowserRouter, Routes, Route } from "react-router-dom";
import Chat from "./pages/Chat";
import Home from "./pages/Home";
import NewGame from './pages/NewGame';
import Game from './pages/Game';
import JoinGame from './pages/JoinGame';

function App() {

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/">
          <Route index element={<Home />} />
          <Route path="chat" element={<Chat />} />
          <Route path="game" element={<Game />} />
          <Route path="newGame" element={<NewGame />} />
          <Route path="joinGame" element={<JoinGame />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;