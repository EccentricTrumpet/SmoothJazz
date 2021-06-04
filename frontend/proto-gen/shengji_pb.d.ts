// package: grpc.testing
// file: shengji.proto

import * as jspb from "google-protobuf";

export class AddAIPlayerRequest extends jspb.Message {
  getGameId(): string;
  setGameId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): AddAIPlayerRequest.AsObject;
  static toObject(includeInstance: boolean, msg: AddAIPlayerRequest): AddAIPlayerRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: AddAIPlayerRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): AddAIPlayerRequest;
  static deserializeBinaryFromReader(message: AddAIPlayerRequest, reader: jspb.BinaryReader): AddAIPlayerRequest;
}

export namespace AddAIPlayerRequest {
  export type AsObject = {
    gameId: string,
  }
}

export class AddAIPlayerResponse extends jspb.Message {
  getPlayerName(): string;
  setPlayerName(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): AddAIPlayerResponse.AsObject;
  static toObject(includeInstance: boolean, msg: AddAIPlayerResponse): AddAIPlayerResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: AddAIPlayerResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): AddAIPlayerResponse;
  static deserializeBinaryFromReader(message: AddAIPlayerResponse, reader: jspb.BinaryReader): AddAIPlayerResponse;
}

export namespace AddAIPlayerResponse {
  export type AsObject = {
    playerName: string,
  }
}

export class EnterRoomRequest extends jspb.Message {
  getGameId(): string;
  setGameId(value: string): void;

  getPlayerId(): string;
  setPlayerId(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): EnterRoomRequest.AsObject;
  static toObject(includeInstance: boolean, msg: EnterRoomRequest): EnterRoomRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: EnterRoomRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): EnterRoomRequest;
  static deserializeBinaryFromReader(message: EnterRoomRequest, reader: jspb.BinaryReader): EnterRoomRequest;
}

export namespace EnterRoomRequest {
  export type AsObject = {
    gameId: string,
    playerId: string,
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

export class PlayHandRequest extends jspb.Message {
  getPlayerId(): string;
  setPlayerId(value: string): void;

  getGameId(): string;
  setGameId(value: string): void;

  getIntention(): PlayHandRequest.IntentionMap[keyof PlayHandRequest.IntentionMap];
  setIntention(value: PlayHandRequest.IntentionMap[keyof PlayHandRequest.IntentionMap]): void;

  hasHand(): boolean;
  clearHand(): void;
  getHand(): Hand | undefined;
  setHand(value?: Hand): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): PlayHandRequest.AsObject;
  static toObject(includeInstance: boolean, msg: PlayHandRequest): PlayHandRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: PlayHandRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): PlayHandRequest;
  static deserializeBinaryFromReader(message: PlayHandRequest, reader: jspb.BinaryReader): PlayHandRequest;
}

export namespace PlayHandRequest {
  export type AsObject = {
    playerId: string,
    gameId: string,
    intention: PlayHandRequest.IntentionMap[keyof PlayHandRequest.IntentionMap],
    hand?: Hand.AsObject,
  }

  export interface IntentionMap {
    CLAIM_TRUMP: 0;
    PLAY_HAND: 1;
    HIDE_KITTY: 2;
  }

  export const Intention: IntentionMap;
}

export class PlayHandResponse extends jspb.Message {
  getSuccess(): boolean;
  setSuccess(value: boolean): void;

  getErrorMessage(): string;
  setErrorMessage(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): PlayHandResponse.AsObject;
  static toObject(includeInstance: boolean, msg: PlayHandResponse): PlayHandResponse.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: PlayHandResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): PlayHandResponse;
  static deserializeBinaryFromReader(message: PlayHandResponse, reader: jspb.BinaryReader): PlayHandResponse;
}

export namespace PlayHandResponse {
  export type AsObject = {
    success: boolean,
    errorMessage: string,
  }
}

export class Player extends jspb.Message {
  getPlayerId(): string;
  setPlayerId(value: string): void;

  hasCardsOnHand(): boolean;
  clearCardsOnHand(): void;
  getCardsOnHand(): Hand | undefined;
  setCardsOnHand(value?: Hand): void;

  hasWinningPile(): boolean;
  clearWinningPile(): void;
  getWinningPile(): Hand | undefined;
  setWinningPile(value?: Hand): void;

  hasCurrentRoundTrick(): boolean;
  clearCurrentRoundTrick(): void;
  getCurrentRoundTrick(): Hand | undefined;
  setCurrentRoundTrick(value?: Hand): void;

  getScore(): number;
  setScore(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): Player.AsObject;
  static toObject(includeInstance: boolean, msg: Player): Player.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: Player, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): Player;
  static deserializeBinaryFromReader(message: Player, reader: jspb.BinaryReader): Player;
}

export namespace Player {
  export type AsObject = {
    playerId: string,
    cardsOnHand?: Hand.AsObject,
    winningPile?: Hand.AsObject,
    currentRoundTrick?: Hand.AsObject,
    score: number,
  }
}

export class Game extends jspb.Message {
  getGameId(): string;
  setGameId(value: string): void;

  getCreatorPlayerId(): string;
  setCreatorPlayerId(value: string): void;

  getDealerPlayerId(): string;
  setDealerPlayerId(value: string): void;

  getNextTurnPlayerId(): string;
  setNextTurnPlayerId(value: string): void;

  getCurrentRoundWinnerPlayerId(): string;
  setCurrentRoundWinnerPlayerId(value: string): void;

  clearPlayersList(): void;
  getPlayersList(): Array<Player>;
  setPlayersList(value: Array<Player>): void;
  addPlayers(value?: Player, index?: number): Player;

  hasKitty(): boolean;
  clearKitty(): void;
  getKitty(): Hand | undefined;
  setKitty(value?: Hand): void;

  getTrumpSuit(): Card.SuitMap[keyof Card.SuitMap];
  setTrumpSuit(value: Card.SuitMap[keyof Card.SuitMap]): void;

  getTrumpNum(): Card.NumMap[keyof Card.NumMap];
  setTrumpNum(value: Card.NumMap[keyof Card.NumMap]): void;

  getDeckCardCount(): number;
  setDeckCardCount(value: number): void;

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
    dealerPlayerId: string,
    nextTurnPlayerId: string,
    currentRoundWinnerPlayerId: string,
    playersList: Array<Player.AsObject>,
    kitty?: Hand.AsObject,
    trumpSuit: Card.SuitMap[keyof Card.SuitMap],
    trumpNum: Card.NumMap[keyof Card.NumMap],
    deckCardCount: number,
  }
}

export class Card extends jspb.Message {
  getSuit(): Card.SuitMap[keyof Card.SuitMap];
  setSuit(value: Card.SuitMap[keyof Card.SuitMap]): void;

  getNum(): Card.NumMap[keyof Card.NumMap];
  setNum(value: Card.NumMap[keyof Card.NumMap]): void;

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
    suit: Card.SuitMap[keyof Card.SuitMap],
    num: Card.NumMap[keyof Card.NumMap],
  }

  export interface SuitMap {
    SUIT_UNDEFINED: 0;
    HEARTS: 1;
    SPADES: 2;
    CLUBS: 3;
    DIAMONDS: 4;
    SMALL_JOKER: 5;
    BIG_JOKER: 6;
  }

  export const Suit: SuitMap;

  export interface NumMap {
    NUM_UNDEFINED: 0;
    ACE: 1;
    TWO: 2;
    THREE: 3;
    FOUR: 4;
    FIVE: 5;
    SIX: 6;
    SEVEN: 7;
    EIGHT: 8;
    NINE: 9;
    TEN: 10;
    JACK: 11;
    QUEEN: 12;
    KING: 13;
  }

  export const Num: NumMap;
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

