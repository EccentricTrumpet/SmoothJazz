import { Constants } from "../Constants";
import { Zone } from "../abstractions/Zone";
import { IController } from "../abstractions/IController";
import { Position } from "../abstractions/Position";
import { PlayerState } from "../abstractions/PlayerState";
import CardComponent from "./CardComponent";
import { DisplaySettings } from "../abstractions/DisplaySettings";
import { SeatPosition } from "../abstractions/SeatPosition";
import { CardState } from "../abstractions/CardState";

interface HandZoneArgument {
  player: PlayerState;
  zone: Zone;
  settings: DisplaySettings;
  controller: IController;
}

const HandZone: React.FC<HandZoneArgument> = ({player, zone, settings, controller}) => {

  let displayRange = 0;
  let displayStart = 0;
  let displayIncrement = 0;

  switch(player.seatPosition) {
    case SeatPosition.North:
    case SeatPosition.South:
      displayRange =
        player.hand.length === 1
          ? Constants.cardWidth
          : Math.min(zone.size.width, Constants.cardOverlap*(player.hand.length - 1) + Constants.cardWidth);
      displayIncrement =
        player.hand.length === 1
          ? 0
          : Math.min(Constants.cardOverlap, (displayRange - Constants.cardWidth)/(player.hand.length-1));
      displayStart = zone.center().x - displayRange/2;
      for (let i = 0; i < player.hand.length; i++) {
        player.hand[i].state = new CardState(
          false,
          false,
          0,
          new Position(displayStart + i*displayIncrement, zone.position.y),
        );
      }
      break;
    case SeatPosition.East:
      displayRange =
        player.hand.length === 1
          ? Constants.cardWidth
          : Math.min(zone.size.height, Constants.cardOverlap*(player.hand.length - 1) + Constants.cardWidth);
      displayIncrement =
        player.hand.length === 1
          ? 0
          : Math.min(Constants.cardOverlap, (displayRange - Constants.cardWidth)/(player.hand.length-1));
      displayStart = zone.center().y + displayRange/2 - Constants.cardHeight + (Constants.cardHeight - Constants.cardWidth)/2;
      for (let i = 0; i < player.hand.length; i++) {
        player.hand[i].state = new CardState(
          false,
          false,
          -90,
          new Position(zone.center().x - Constants.cardWidth/2, displayStart - i*displayIncrement),
        );
      }
      break;
    case SeatPosition.West:
      displayRange =
        player.hand.length === 1
          ? Constants.cardWidth
          : Math.min(zone.size.height, Constants.cardOverlap*(player.hand.length - 1) + Constants.cardWidth);
      displayIncrement =
        player.hand.length === 1
          ? 0
          : Math.min(Constants.cardOverlap, (displayRange - Constants.cardWidth)/(player.hand.length-1));
      displayStart = zone.center().y - displayRange/2- (Constants.cardHeight - Constants.cardWidth)/2;
      for (let i = 0; i < player.hand.length; i++) {
        player.hand[i].state = new CardState(
          false,
          false,
          90,
          new Position(zone.center().x - Constants.cardWidth/2, displayStart + i*displayIncrement),
        );
      }
      break;
  }

  return (
    <div className="container" style={{
      position: "fixed",
      left: zone.position.x,
      top: zone.position.y,
      width: zone.size.width,
      height: zone.size.height,
      backgroundColor: Constants.backgroundColor,
    }}>
      { player.hand.map((card, idx) => {
        return <CardComponent key={card.id} idx={idx} card={card} settings={settings} onClick={() => {
          controller.onPlayCard(card);
        }} />
      })}
    </div>
  );
}

export default HandZone;
