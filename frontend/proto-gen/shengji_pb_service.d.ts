// package: grpc.testing
// file: shengji.proto

import * as shengji_pb from "./shengji_pb";
import {grpc} from "@improbable-eng/grpc-web";

type ShengjiCreateGame = {
  readonly methodName: string;
  readonly service: typeof Shengji;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof shengji_pb.CreateGameRequest;
  readonly responseType: typeof shengji_pb.Game;
};

type ShengjiEnterRoom = {
  readonly methodName: string;
  readonly service: typeof Shengji;
  readonly requestStream: false;
  readonly responseStream: true;
  readonly requestType: typeof shengji_pb.EnterRoomRequest;
  readonly responseType: typeof shengji_pb.Game;
};

type ShengjiPlayHand = {
  readonly methodName: string;
  readonly service: typeof Shengji;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof shengji_pb.PlayHandRequest;
  readonly responseType: typeof shengji_pb.PlayHandResponse;
};

type ShengjiAddAIPlayer = {
  readonly methodName: string;
  readonly service: typeof Shengji;
  readonly requestStream: false;
  readonly responseStream: false;
  readonly requestType: typeof shengji_pb.AddAIPlayerRequest;
  readonly responseType: typeof shengji_pb.AddAIPlayerResponse;
};

export class Shengji {
  static readonly serviceName: string;
  static readonly CreateGame: ShengjiCreateGame;
  static readonly EnterRoom: ShengjiEnterRoom;
  static readonly PlayHand: ShengjiPlayHand;
  static readonly AddAIPlayer: ShengjiAddAIPlayer;
}

export type ServiceError = { message: string, code: number; metadata: grpc.Metadata }
export type Status = { details: string, code: number; metadata: grpc.Metadata }

interface UnaryResponse {
  cancel(): void;
}
interface ResponseStream<T> {
  cancel(): void;
  on(type: 'data', handler: (message: T) => void): ResponseStream<T>;
  on(type: 'end', handler: (status?: Status) => void): ResponseStream<T>;
  on(type: 'status', handler: (status: Status) => void): ResponseStream<T>;
}
interface RequestStream<T> {
  write(message: T): RequestStream<T>;
  end(): void;
  cancel(): void;
  on(type: 'end', handler: (status?: Status) => void): RequestStream<T>;
  on(type: 'status', handler: (status: Status) => void): RequestStream<T>;
}
interface BidirectionalStream<ReqT, ResT> {
  write(message: ReqT): BidirectionalStream<ReqT, ResT>;
  end(): void;
  cancel(): void;
  on(type: 'data', handler: (message: ResT) => void): BidirectionalStream<ReqT, ResT>;
  on(type: 'end', handler: (status?: Status) => void): BidirectionalStream<ReqT, ResT>;
  on(type: 'status', handler: (status: Status) => void): BidirectionalStream<ReqT, ResT>;
}

export class ShengjiClient {
  readonly serviceHost: string;

  constructor(serviceHost: string, options?: grpc.RpcOptions);
  createGame(
    requestMessage: shengji_pb.CreateGameRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: shengji_pb.Game|null) => void
  ): UnaryResponse;
  createGame(
    requestMessage: shengji_pb.CreateGameRequest,
    callback: (error: ServiceError|null, responseMessage: shengji_pb.Game|null) => void
  ): UnaryResponse;
  enterRoom(requestMessage: shengji_pb.EnterRoomRequest, metadata?: grpc.Metadata): ResponseStream<shengji_pb.Game>;
  playHand(
    requestMessage: shengji_pb.PlayHandRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: shengji_pb.PlayHandResponse|null) => void
  ): UnaryResponse;
  playHand(
    requestMessage: shengji_pb.PlayHandRequest,
    callback: (error: ServiceError|null, responseMessage: shengji_pb.PlayHandResponse|null) => void
  ): UnaryResponse;
  addAIPlayer(
    requestMessage: shengji_pb.AddAIPlayerRequest,
    metadata: grpc.Metadata,
    callback: (error: ServiceError|null, responseMessage: shengji_pb.AddAIPlayerResponse|null) => void
  ): UnaryResponse;
  addAIPlayer(
    requestMessage: shengji_pb.AddAIPlayerRequest,
    callback: (error: ServiceError|null, responseMessage: shengji_pb.AddAIPlayerResponse|null) => void
  ): UnaryResponse;
}

