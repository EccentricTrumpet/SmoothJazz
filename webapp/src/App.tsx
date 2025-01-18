import { BrowserRouter, Route, Routes } from "react-router-dom";
import HomePage from "./pages/HomePage";
import JoinMatchPage from './pages/JoinMatchPage';
import MatchPage from './pages/MatchPage';
import NewMatchPage from './pages/NewMatchPage';

function App() {

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/">
          <Route index element={<HomePage />} />
          <Route path="/:id" element={<MatchPage />} />
          <Route path="/newMatch" element={<NewMatchPage />} />
          <Route path="/joinMatch" element={<JoinMatchPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;