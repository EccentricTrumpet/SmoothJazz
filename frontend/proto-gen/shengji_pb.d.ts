// package: grpc.testing
// file: shengji.proto

import * as jspb from "google-protobuf";

export class StreamGameRequest extends jspb.Message {
  getGameId(): string;
  setGameId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): StreamGameRequest.AsObject;
  static toObject(includeInstance: boolean, msg: StreamGameRequest): StreamGameRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: StreamGameRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): StreamGameRequest;
  static deserializeBinaryFromReader(message: StreamGameRequest, reader: jspb.BinaryReader): StreamGameRequest;
}

export namespace StreamGameRequest {
  export type AsObject = {
    gameId: string,
  }
}

export class CreateGameRequest extends jspb.Message {
  getPlayerId(): string;
  setPlayerId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): CreateGameRequest.AsObject;
  static toObject(includeInstance: boolean, msg: CreateGameRequest): CreateGameRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: CreateGameRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): CreateGameRequest;
  static deserializeBinaryFromReader(message: CreateGameRequest, reader: jspb.BinaryReader): CreateGameRequest;
}

export namespace CreateGameRequest {
  export type AsObject = {
    playerId: string,
  }
}

export class JoinGameRequest extends jspb.Message {
  getPlayerId(): string;
  setPlayerId(value: string): void;

  getGameId(): string;
  setGameId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): JoinGameRequest.AsObject;
  static toObject(includeInstance: boolean, msg: JoinGameRequest): JoinGameRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: JoinGameRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): JoinGameRequest;
  static deserializeBinaryFromReader(message: JoinGameRequest, reader: jspb.BinaryReader): JoinGameRequest;
}

export namespace JoinGameRequest {
  export type AsObject = {
    playerId: string,
    gameId: string,
  }
}

export class LeaveGameRequest extends jspb.Message {
  getPlayerId(): string;
  setPlayerId(value: string): void;

  getGameId(): string;
  setGameId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): LeaveGameRequest.AsObject;
  static toObject(includeInstance: boolean, msg: LeaveGameRequest): LeaveGameRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: LeaveGameRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): LeaveGameRequest;
  static deserializeBinaryFromReader(message: LeaveGameRequest, reader: jspb.BinaryReader): LeaveGameRequest;
}

export namespace LeaveGameRequest {
  export type AsObject = {
    playerId: string,
    gameId: string,
  }
}

export class PauseGameRequest extends jspb.Message {
  getPlayerId(): string;
  setPlayerId(value: string): void;

  getGameId(): string;
  setGameId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): PauseGameRequest.AsObject;
  static toObject(includeInstance: boolean, msg: PauseGameRequest): PauseGameRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: PauseGameRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): PauseGameRequest;
  static deserializeBinaryFromReader(message: PauseGameRequest, reader: jspb.BinaryReader): PauseGameRequest;
}

export namespace PauseGameRequest {
  export type AsObject = {
    playerId: string,
    gameId: string,
  }
}

export class ResumeGameRequest extends jspb.Message {
  getPlayerId(): string;
  setPlayerId(value: string): void;

  getGameId(): string;
  setGameId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ResumeGameRequest.AsObject;
  static toObject(includeInstance: boolean, msg: ResumeGameRequest): ResumeGameRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ResumeGameRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ResumeGameRequest;
  static deserializeBinaryFromReader(message: ResumeGameRequest, reader: jspb.BinaryReader): ResumeGameRequest;
}

export namespace ResumeGameRequest {
  export type AsObject = {
    playerId: string,
    gameId: string,
  }
}

export class StartGameRequest extends jspb.Message {
  getPlayerId(): string;
  setPlayerId(value: string): void;

  getGameId(): string;
  setGameId(value: string): void;

  clearOrderedPlayerIdsList(): void;
  getOrderedPlayerIdsList(): Array<string>;
  setOrderedPlayerIdsList(value: Array<string>): void;
  addOrderedPlayerIds(value: string, index?: number): string;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): StartGameRequest.AsObject;
  static toObject(includeInstance: boolean, msg: StartGameRequest): StartGameRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: StartGameRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): StartGameRequest;
  static deserializeBinaryFromReader(message: StartGameRequest, reader: jspb.BinaryReader): StartGameRequest;
}

export namespace StartGameRequest {
  export type AsObject = {
    playerId: string,
    gameId: string,
    orderedPlayerIdsList: Array<string>,
  }
}

export class PlayGameRequest extends jspb.Message {
  getPlayerId(): string;
  setPlayerId(value: string): void;

  getGameId(): string;
  setGameId(value: string): void;

  clearHandList(): void;
  getHandList(): Array<Card>;
  setHandList(value: Array<Card>): void;
  addHand(value?: Card, index?: number): Card;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): PlayGameRequest.AsObject;
  static toObject(includeInstance: boolean, msg: PlayGameRequest): PlayGameRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: PlayGameRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): PlayGameRequest;
  static deserializeBinaryFromReader(message: PlayGameRequest, reader: jspb.BinaryReader): PlayGameRequest;
}

export namespace PlayGameRequest {
  export type AsObject = {
    playerId: string,
    gameId: string,
    handList: Array<Card.AsObject>,
  }
}

export class Card extends jspb.Message {
  hasCard(): boolean;
  clearCard(): void;
  getCard(): Card.RegularCard | undefined;
  setCard(value?: Card.RegularCard): void;

  hasIsSmallJoker(): boolean;
  clearIsSmallJoker(): void;
  getIsSmallJoker(): boolean;
  setIsSmallJoker(value: boolean): void;

  hasIsBigJoker(): boolean;
  clearIsBigJoker(): void;
  getIsBigJoker(): boolean;
  setIsBigJoker(value: boolean): void;

  getActualcardCase(): Card.ActualcardCase;
  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): Card.AsObject;
  static toObject(includeInstance: boolean, msg: Card): Card.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: Card, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): Card;
  static deserializeBinaryFromReader(message: Card, reader: jspb.BinaryReader): Card;
}

export namespace Card {
  export type AsObject = {
    card?: Card.RegularCard.AsObject,
    isSmallJoker: boolean,
    isBigJoker: boolean,
  }

  export class RegularCard extends jspb.Message {
    getSuit(): Card.SuitMap[keyof Card.SuitMap];
    setSuit(value: Card.SuitMap[keyof Card.SuitMap]): void;

    getNum(): Card.NumMap[keyof Card.NumMap];
    setNum(value: Card.NumMap[keyof Card.NumMap]): void;

    serializeBinary(): Uint8Array;
    toObject(includeInstance?: boolean): RegularCard.AsObject;
    static toObject(includeInstance: boolean, msg: RegularCard): RegularCard.AsObject;
    static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
    static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
    static serializeBinaryToWriter(message: RegularCard, writer: jspb.BinaryWriter): void;
    static deserializeBinary(bytes: Uint8Array): RegularCard;
    static deserializeBinaryFromReader(message: RegularCard, reader: jspb.BinaryReader): RegularCard;
  }

  export namespace RegularCard {
    export type AsObject = {
      suit: Card.SuitMap[keyof Card.SuitMap],
      num: Card.NumMap[keyof Card.NumMap],
    }
  }

  export interface SuitMap {
    UNDEFINED: 0;
    HEATS: 1;
    SPADES: 2;
    CLUBS: 3;
    DIAMONDS: 4;
  }

  export const Suit: SuitMap;

  export interface NumMap {
    ACE: 0;
    TWO: 1;
    THREE: 2;
    FOUR: 3;
    FIVE: 4;
    SIX: 5;
    SEVEN: 6;
    EIGHT: 7;
    NINE: 8;
    TEN: 9;
    JACK: 10;
    QUEEN: 11;
    KING: 12;
  }

  export const Num: NumMap;

  export enum ActualcardCase {
    ACTUALCARD_NOT_SET = 0,
    CARD = 1,
    IS_SMALL_JOKER = 2,
    IS_BIG_JOKER = 3,
  }
}

export class Hand extends jspb.Message {
  clearCardsList(): void;
  getCardsList(): Array<Card>;
  setCardsList(value: Array<Card>): void;
  addCards(value?: Card, index?: number): Card;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): Hand.AsObject;
  static toObject(includeInstance: boolean, msg: Hand): Hand.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: Hand, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): Hand;
  static deserializeBinaryFromReader(message: Hand, reader: jspb.BinaryReader): Hand;
}

export namespace Hand {
  export type AsObject = {
    cardsList: Array<Card.AsObject>,
  }
}

export class Game extends jspb.Message {
  getGameId(): string;
  setGameId(value: string): void;

  getCreatorPlayerId(): string;
  setCreatorPlayerId(value: string): void;

  clearPlayerIdsList(): void;
  getPlayerIdsList(): Array<string>;
  setPlayerIdsList(value: Array<string>): void;
  addPlayerIds(value: string, index?: number): string;

  getTeammateId(): string;
  setTeammateId(value: string): void;

  hasData(): boolean;
  clearData(): void;
  getData(): GameData | undefined;
  setData(value?: GameData): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): Game.AsObject;
  static toObject(includeInstance: boolean, msg: Game): Game.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: Game, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): Game;
  static deserializeBinaryFromReader(message: Game, reader: jspb.BinaryReader): Game;
}

export namespace Game {
  export type AsObject = {
    gameId: string,
    creatorPlayerId: string,
    playerIdsList: Array<string>,
    teammateId: string,
    data?: GameData.AsObject,
  }
}

export class GameData extends jspb.Message {
  getState(): GameData.GameStateMap[keyof GameData.GameStateMap];
  setState(value: GameData.GameStateMap[keyof GameData.GameStateMap]): void;

  getWaitingForPlayerId(): string;
  setWaitingForPlayerId(value: string): void;

  getGameActionCount(): number;
  setGameActionCount(value: number): void;

  getTrumpSuit(): Card.SuitMap[keyof Card.SuitMap];
  setTrumpSuit(value: Card.SuitMap[keyof Card.SuitMap]): void;

  getTrumpNum(): Card.NumMap[keyof Card.NumMap];
  setTrumpNum(value: Card.NumMap[keyof Card.NumMap]): void;

  hasMyHandCards(): boolean;
  clearMyHandCards(): void;
  getMyHandCards(): Hand | undefined;
  setMyHandCards(value?: Hand): void;

  getCardsOnTableMap(): jspb.Map<string, Hand>;
  clearCardsOnTableMap(): void;
  getCurrentScoresMap(): jspb.Map<string, number>;
  clearCurrentScoresMap(): void;
  getCumulativeScoresMap(): jspb.Map<string, number>;
  clearCumulativeScoresMap(): void;
  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GameData.AsObject;
  static toObject(includeInstance: boolean, msg: GameData): GameData.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GameData, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GameData;
  static deserializeBinaryFromReader(message: GameData, reader: jspb.BinaryReader): GameData;
}

export namespace GameData {
  export type AsObject = {
    state: GameData.GameStateMap[keyof GameData.GameStateMap],
    waitingForPlayerId: string,
    gameActionCount: number,
    trumpSuit: Card.SuitMap[keyof Card.SuitMap],
    trumpNum: Card.NumMap[keyof Card.NumMap],
    myHandCards?: Hand.AsObject,
    cardsOnTableMap: Array<[string, Hand.AsObject]>,
    currentScoresMap: Array<[string, number]>,
    cumulativeScoresMap: Array<[string, number]>,
  }

  export interface GameStateMap {
    UNDEFINED: 0;
    NOT_ENOUGH_PLAYERS: 1;
    NOT_STARTED: 2;
    STARTED: 3;
    PAUSED: 4;
    ENDED: 5;
  }

  export const GameState: GameStateMap;
}

