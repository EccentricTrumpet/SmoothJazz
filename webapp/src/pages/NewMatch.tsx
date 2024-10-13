import { useEffect, useState } from 'react';
import { CookiesProvider, useCookies } from 'react-cookie'
import { Options } from '../scripts/Options'
import { useNavigate } from 'react-router-dom';

export default function NewMatch() {
  const [cookie, setCookie] = useCookies(['shengji'])
  const [options, setOptions] = useState(Options);
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
    const value = event.target.type === 'checkbox' ? event.target.checked : event.target.value;
    setOptions(values => ({...values, [name]: value}));
  }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setCookie('shengji', options, { path: '/'});
    const name = options.name
    const response = await fetch('http://localhost:5001/match', {
      method: 'POST',
      headers:new Headers({
        'Content-type': 'application/json'
      }),
      body: JSON.stringify(options)
    });
    const match_id = parseInt(await response.text());
    navigate(`/${match_id}`, { state: { name: name } });
  }

  return (
    <CookiesProvider>
      <h1>Create a new match</h1>
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
        <details>
          <summary>Settings</summary>
          <fieldset>
            <label htmlFor="speed">Speed</label>
            <input
              id="speed"
              name="speed"
              list="speeds"
              type="range"
              min="1"
              max="5"
              step="1"
              value={options.speed || "3"}
              onChange={handleChange}
            />
          </fieldset>
          <fieldset>
            <label htmlFor="debug">
              <input
                type="checkbox"
                role="switch"
                id="debug"
                name="debug"
                checked={options.debug || false}
                onChange={handleChange}
              />
              Debug mode
            </label>
          </fieldset>
        </details>
        <button type="submit">
          Start
        </button>
      </form>
    </CookiesProvider>
  );
}
