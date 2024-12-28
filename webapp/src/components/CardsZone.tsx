import { ControllerInterface } from "../abstractions/ControllerInterface";
import { Position, Zone } from "../abstractions/bounds";
import { Seat } from "../abstractions/enums";
import { OptionsState, TrumpState } from "../abstractions/states";
import { Constants } from "../Constants";
import { CardComponent } from ".";
import { Card } from "../abstractions";

interface CardsZoneInputs {
  cards: Card[];
  seat: Seat;
  trumpState: TrumpState;
  zone: Zone;
  options: OptionsState;
  controller?: ControllerInterface | undefined;
}

export const CardsZone: React.FC<CardsZoneInputs> = ({cards, seat, trumpState, zone, options, controller = undefined}) => {
  // Sort cards for display
  cards.sort((a, b) => trumpState.getDisplayOrder(a) - trumpState.getDisplayOrder(b));

  let [xStart, yStart, dx, dy, xSelected, ySelected, rotate] = [0, 0, 0, 0, 0, 0, 0]

  if (seat === Seat.East) {
    const range = cards.length === 1 ? Constants.cardWidth
      : Math.min(zone.size.height, Constants.cardOverlap*(cards.length - 1) + Constants.cardWidth);
    xStart = zone.center().x - Constants.cardWidth/2;
    yStart = zone.center().y + range/2 - Constants.cardHeight/2 - Constants.cardWidth/2;
    dy = cards.length === 1 ? 0
      : -Math.min(Constants.cardOverlap, (range - Constants.cardWidth)/(cards.length-1));
    xSelected = -Constants.cardOverlap;
    rotate = -90;
  } else if (seat === Seat.West) {
    const range = cards.length === 1 ? Constants.cardWidth
      : Math.min(zone.size.height, Constants.cardOverlap*(cards.length - 1) + Constants.cardWidth);
    xStart = zone.center().x - Constants.cardWidth/2;
    yStart = zone.center().y - range/2 - Constants.cardHeight/2 + Constants.cardWidth/2;
    dy = cards.length === 1 ? 0
      : Math.min(Constants.cardOverlap, (range - Constants.cardWidth)/(cards.length-1));
    xSelected = Constants.cardOverlap;
    rotate = 90;
  } else {
    const range = cards.length === 1 ? Constants.cardWidth
      : Math.min(zone.size.width, Constants.cardOverlap*(cards.length - 1) + Constants.cardWidth);
    xStart = zone.center().x - range/2;
    yStart = zone.top();
    dx = cards.length === 1 ? 0
      : Math.min(Constants.cardOverlap, (range - Constants.cardWidth)/(cards.length-1));
    ySelected = seat === Seat.North ? Constants.cardOverlap : -Constants.cardOverlap;
  }

  for (let i = 0; i < cards.length; i++) {
    cards[i].state.rotate = rotate;
    cards[i].state.position = new Position(xStart + i*dx, yStart + i*dy);
    cards[i].state.offset = cards[i].state.selected ? new Position(xSelected, ySelected) : new Position(0, 0);
  }

  return (
    <div className="container" style={{
      position: "fixed",
      left: zone.left(),
      top: zone.top(),
      width: zone.size.width,
      maxWidth: "none",
      height: zone.size.height,
      backgroundColor: Constants.backgroundColor,
    }}>
      { cards.map((card, idx) => {
        return <CardComponent key={card.id} idx={idx} card={card} options={options} onClick={() => controller?.onSelect(card)} />
      })}
    </div>
  );
}
