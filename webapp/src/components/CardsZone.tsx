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
  controller: ControllerInterface;
}

export const CardsZone: React.FC<CardsZoneInputs> = ({cards, seat, trumpState, zone, options, controller}) => {
  // Sort cards for display
  cards.sort((a, b) => trumpState.getSortOrder(a) - trumpState.getSortOrder(b));

  let displayRange = 0;
  let displayStart = 0;
  let displayIncrement = 0;

  switch(seat) {
    case Seat.North:
      displayRange =
        cards.length === 1
          ? Constants.cardWidth
          : Math.min(zone.size.width, Constants.cardOverlap*(cards.length - 1) + Constants.cardWidth);
      displayIncrement =
        cards.length === 1
          ? 0
          : Math.min(Constants.cardOverlap, (displayRange - Constants.cardWidth)/(cards.length-1));
      displayStart = zone.center().x - displayRange/2;
      for (let i = 0; i < cards.length; i++) {
        cards[i].state.position = new Position(displayStart + i*displayIncrement, zone.top());
        cards[i].state.offset = cards[i].state.selected
          ? new Position(0, Constants.margin)
          : new Position(0, 0);
      }
      break;
    case Seat.South:
      displayRange =
        cards.length === 1
          ? Constants.cardWidth
          : Math.min(zone.size.width, Constants.cardOverlap*(cards.length - 1) + Constants.cardWidth);
      displayIncrement =
        cards.length === 1
          ? 0
          : Math.min(Constants.cardOverlap, (displayRange - Constants.cardWidth)/(cards.length-1));
      displayStart = zone.center().x - displayRange/2;
      for (let i = 0; i < cards.length; i++) {
        cards[i].state.position = new Position(displayStart + i*displayIncrement, zone.top());
        cards[i].state.offset = cards[i].state.selected
          ? new Position(0, -Constants.margin)
          : new Position(0, 0);
      }
      break;
    case Seat.East:
      displayRange =
        cards.length === 1
          ? Constants.cardWidth
          : Math.min(zone.size.height, Constants.cardOverlap*(cards.length - 1) + Constants.cardWidth);
      displayIncrement =
        cards.length === 1
          ? 0
          : Math.min(Constants.cardOverlap, (displayRange - Constants.cardWidth)/(cards.length-1));
      displayStart = zone.center().y + displayRange/2 - Constants.cardHeight + (Constants.cardHeight - Constants.cardWidth)/2;
      for (let i = 0; i < cards.length; i++) {
        cards[i].state.rotate = -90;
        cards[i].state.position = new Position(zone.center().x - Constants.cardWidth/2, displayStart - i*displayIncrement);
        cards[i].state.offset = cards[i].state.selected
          ? new Position(-Constants.margin, 0)
          : new Position(0, 0);
      }
      break;
    case Seat.West:
      displayRange =
        cards.length === 1
          ? Constants.cardWidth
          : Math.min(zone.size.height, Constants.cardOverlap*(cards.length - 1) + Constants.cardWidth);
      displayIncrement =
        cards.length === 1
          ? 0
          : Math.min(Constants.cardOverlap, (displayRange - Constants.cardWidth)/(cards.length-1));
      displayStart = zone.center().y - displayRange/2- (Constants.cardHeight - Constants.cardWidth)/2;
      for (let i = 0; i < cards.length; i++) {
        cards[i].state.rotate = 90;
        cards[i].state.position = new Position(zone.center().x - Constants.cardWidth/2, displayStart + i*displayIncrement);
        cards[i].state.offset = cards[i].state.selected
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
      { cards.map((card, idx) => {
        return <CardComponent key={card.id} idx={idx} card={card} options={options} onClick={() => {
          controller.onSelect(card);
        }} />
      })}
    </div>
  );
}
