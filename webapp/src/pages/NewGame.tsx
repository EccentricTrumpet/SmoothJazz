import { useEffect, useState } from 'react';
import { CookiesProvider, useCookies } from 'react-cookie'
import { Options } from '../scripts/Options'

export default function NewGame() {
  const [cookie, setCookie] = useCookies(['shengji'])
  const [options, setOptions] = useState(Options);

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
    const value = event.target.type === 'checkbox' ? event.target.checked : event.target.value;
    setOptions(values => ({...values, [name]: value}));
  }

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setCookie('shengji', options, { path: '/'});
  }

  return (
    <CookiesProvider>
      <h1>Create a new game</h1>
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
