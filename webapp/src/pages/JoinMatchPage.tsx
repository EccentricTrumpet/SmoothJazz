import { useEffect, useState } from 'react';
import { CookiesProvider, useCookies } from 'react-cookie'
import { Options } from '../scripts/Options'
import { useNavigate } from 'react-router-dom';

export default function JoinMatchPage() {
  const [cookie, setCookie] = useCookies(['shengji'])
  const [options, setOptions] = useState(Options());
  const [match, setMatch] = useState(-1);
  const navigate = useNavigate()

  useEffect(() => {
    const savedOptions = cookie['shengji'];
    setOptions({
      name: savedOptions?.['name'] || "",
      speed: savedOptions?.['speed'] || "",
      debug: savedOptions?.['debug'] || false
    });
  }, [cookie])

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const name = event.target.name;
    const value = event.target.value;
    setOptions(values => ({...values, [name]: value}));
  }

  const handleMatchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setMatch(parseInt(event.target.value));
  }

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setCookie('shengji', options, { path: '/'})
    navigate(`/${match}`, { state: { name: options.name } });
  }

  return (
    <div className="container">
      <CookiesProvider>
        <h1>Join a match</h1>
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
          <label htmlFor="match">Match</label>
          <input
            id="match"
            type="number"
            name="match"
            placeholder="Match"
            onChange={handleMatchChange}
            required
          />

          <button type="submit">
            Join
          </button>
        </form>
      </CookiesProvider>
    </div>
  );
}
