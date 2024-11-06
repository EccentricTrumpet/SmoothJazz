import { ControllerInterface } from "../abstractions/ControllerInterface";
import { Position, Zone } from "../abstractions/bounds";
import { Seat } from "../abstractions/enums";
import { OptionsState, PlayerState } from "../abstractions/states";
import { Constants } from "../Constants";
import { CardComponent } from ".";

interface HandZoneInputs {
  player: PlayerState;
  zone: Zone;
  options: OptionsState;
  controller: ControllerInterface;
}

export const HandZone: React.FC<HandZoneInputs> = ({player, zone, options, controller}) => {

  let displayRange = 0;
  let displayStart = 0;
  let displayIncrement = 0;

  switch(player.seat) {
    case Seat.North:
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
        player.hand[i].state.position = new Position(displayStart + i*displayIncrement, zone.top());
        player.hand[i].state.offset = player.hand[i].state.selected
          ? new Position(0, Constants.margin)
          : new Position(0, 0);
      }
      break;
    case Seat.South:
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
        player.hand[i].state.position = new Position(displayStart + i*displayIncrement, zone.top());
        player.hand[i].state.offset = player.hand[i].state.selected
          ? new Position(0, -Constants.margin)
          : new Position(0, 0);
      }
      break;
    case Seat.East:
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
        player.hand[i].state.rotate = -90;
        player.hand[i].state.position = new Position(zone.center().x - Constants.cardWidth/2, displayStart - i*displayIncrement);
        player.hand[i].state.offset = player.hand[i].state.selected
          ? new Position(-Constants.margin, 0)
          : new Position(0, 0);
      }
      break;
    case Seat.West:
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
        player.hand[i].state.rotate = 90;
        player.hand[i].state.position = new Position(zone.center().x - Constants.cardWidth/2, displayStart + i*displayIncrement);
        player.hand[i].state.offset = player.hand[i].state.selected
          ? new Position(Constants.margin, 0)
          : new Position(0, 0);
      }
      break;
  }

  return (
    <div className="container" style={{
      position: "fixed",
      left: zone.left(),
      top: zone.top(),
      width: zone.size.width,
      height: zone.size.height,
      backgroundColor: Constants.backgroundColor,
    }}>
      { player.hand.map((card, idx) => {
        return <CardComponent key={card.id} idx={idx} card={card} options={options} onClick={() => {
          controller.onSelectCard(card);
        }} />
      })}
    </div>
  );
}
