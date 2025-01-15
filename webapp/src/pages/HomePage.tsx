export default function HomePage() {
  return (
    <div className="container">
      <div className="grid">
        <img
          src="./favicon.png"
          alt={`${process.env.REACT_APP_VERSION}`}
          style={{ margin: "auto", height:500, width:500 }}/>
      </div>
      <div className="grid">
        <a role="button" href="newMatch">New Match</a>
        <a role="button" href="joinMatch">Join Match</a>
        <a role="button" href="https://en.wikipedia.org/wiki/Sheng_ji">Rules</a>
      </div>
    </div>
  );
}
