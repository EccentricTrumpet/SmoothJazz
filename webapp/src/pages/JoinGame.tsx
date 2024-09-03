import { useEffect, useState } from 'react';
import { CookiesProvider, useCookies } from 'react-cookie'
import { Options } from '../scripts/Options'

export default function JoinGame() {
  const [cookie, setCookie] = useCookies(['shengji'])
  const [options, setOptions] = useState(Options());
  const [game, setGame] = useState("");

  useEffect(() => {
    const savedOptions = cookie['shengji'];
    setOptions({
      name: savedOptions['name'] || "",
      speed: savedOptions['speed'] || "",
      debug: savedOptions['debug'] || false
    });
  }, [cookie])

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const name = event.target.name;
    const value = event.target.value;
    setOptions(values => ({...values, [name]: value}));
  }

  const handleGameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setGame(event.target.value);
  }

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setCookie('shengji', options, { path: '/'})
  }

  return (
    <CookiesProvider>
      <h1>Join a game</h1>
      <form onSubmit={handleSubmit}>
        <label htmlFor="name">Player name</label>
        <input
          id="name"
          type="text"
          name="name"
          placeholder="Name"
          value={options.name || ""}
          onChange={handleChange}
          required
        />
        <label htmlFor="game">Game</label>
        <input
          id="game"
          type="text"
          name="game"
          placeholder="Game"
          onChange={handleGameChange}
          required
        />

        <button type="submit">
          Join
        </button>
      </form>
    </CookiesProvider>
  );
}
