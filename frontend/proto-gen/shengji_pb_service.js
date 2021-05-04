// package: grpc.testing
// file: shengji.proto

var shengji_pb = require("./shengji_pb");
var grpc = require("@improbable-eng/grpc-web").grpc;

var Shengji = (function () {
  function Shengji() {}
  Shengji.serviceName = "grpc.testing.Shengji";
  return Shengji;
}());

Shengji.CreateGame = {
  methodName: "CreateGame",
  service: Shengji,
  requestStream: false,
  responseStream: false,
  requestType: shengji_pb.CreateGameRequest,
  responseType: shengji_pb.Game
};

Shengji.EnterRoom = {
  methodName: "EnterRoom",
  service: Shengji,
  requestStream: false,
  responseStream: true,
  requestType: shengji_pb.EnterRoomRequest,
  responseType: shengji_pb.Game
};

Shengji.PlayHand = {
  methodName: "PlayHand",
  service: Shengji,
  requestStream: false,
  responseStream: false,
  requestType: shengji_pb.PlayHandRequest,
  responseType: shengji_pb.PlayHandResponse
};

Shengji.AddAIPlayer = {
  methodName: "AddAIPlayer",
  service: Shengji,
  requestStream: false,
  responseStream: false,
  requestType: shengji_pb.AddAIPlayerRequest,
  responseType: shengji_pb.AddAIPlayerResponse
};

exports.Shengji = Shengji;

function ShengjiClient(serviceHost, options) {
  this.serviceHost = serviceHost;
  this.options = options || {};
}

ShengjiClient.prototype.createGame = function createGame(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(Shengji.CreateGame, {
    request: requestMessage,
    host: this.serviceHost,
    metadata: metadata,
    transport: this.options.transport,
    debug: this.options.debug,
    onEnd: function (response) {
      if (callback) {
        if (response.status !== grpc.Code.OK) {
          var err = new Error(response.statusMessage);
          err.code = response.status;
          err.metadata = response.trailers;
          callback(err, null);
        } else {
          callback(null, response.message);
        }
      }
    }
  });
  return {
    cancel: function () {
      callback = null;
      client.close();
    }
  };
};

ShengjiClient.prototype.enterRoom = function enterRoom(requestMessage, metadata) {
  var listeners = {
    data: [],
    end: [],
    status: []
  };
  var client = grpc.invoke(Shengji.EnterRoom, {
    request: requestMessage,
    host: this.serviceHost,
    metadata: metadata,
    transport: this.options.transport,
    debug: this.options.debug,
    onMessage: function (responseMessage) {
      listeners.data.forEach(function (handler) {
        handler(responseMessage);
      });
    },
    onEnd: function (status, statusMessage, trailers) {
      listeners.status.forEach(function (handler) {
        handler({ code: status, details: statusMessage, metadata: trailers });
      });
      listeners.end.forEach(function (handler) {
        handler({ code: status, details: statusMessage, metadata: trailers });
      });
      listeners = null;
    }
  });
  return {
    on: function (type, handler) {
      listeners[type].push(handler);
      return this;
    },
    cancel: function () {
      listeners = null;
      client.close();
    }
  };
};

ShengjiClient.prototype.playHand = function playHand(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(Shengji.PlayHand, {
    request: requestMessage,
    host: this.serviceHost,
    metadata: metadata,
    transport: this.options.transport,
    debug: this.options.debug,
    onEnd: function (response) {
      if (callback) {
        if (response.status !== grpc.Code.OK) {
          var err = new Error(response.statusMessage);
          err.code = response.status;
          err.metadata = response.trailers;
          callback(err, null);
        } else {
          callback(null, response.message);
        }
      }
    }
  });
  return {
    cancel: function () {
      callback = null;
      client.close();
    }
  };
};

ShengjiClient.prototype.addAIPlayer = function addAIPlayer(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(Shengji.AddAIPlayer, {
    request: requestMessage,
    host: this.serviceHost,
    metadata: metadata,
    transport: this.options.transport,
    debug: this.options.debug,
    onEnd: function (response) {
      if (callback) {
        if (response.status !== grpc.Code.OK) {
          var err = new Error(response.statusMessage);
          err.code = response.status;
          err.metadata = response.trailers;
          callback(err, null);
        } else {
          callback(null, response.message);
        }
      }
    }
  });
  return {
    cancel: function () {
      callback = null;
      client.close();
    }
  };
};

exports.ShengjiClient = ShengjiClient;

