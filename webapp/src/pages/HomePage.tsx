export default function HomePage() {
  return (
    <div>
      <div>
        <img className="home-logo" src="./favicon.png" alt="" />
      </div>
      <div className="grid">
        <a role="button" href="newMatch">New Match</a>
        <a role="button" href="joinMatch">Join Match</a>
        <a role="button" href="https://en.wikipedia.org/wiki/Sheng_ji" target="_blank" rel="noopener noreferrer">Rules</a>
      </div>
    </div>
  );
}
