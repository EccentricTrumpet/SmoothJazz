# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: shengji.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='shengji.proto',
  package='grpc.testing',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\rshengji.proto\x12\x0cgrpc.testing\"%\n\x12\x41\x64\x64\x41IPlayerRequest\x12\x0f\n\x07game_id\x18\x01 \x01(\t\"*\n\x13\x41\x64\x64\x41IPlayerResponse\x12\x13\n\x0bplayer_name\x18\x01 \x01(\t\"6\n\x10\x45nterRoomRequest\x12\x0f\n\x07game_id\x18\x01 \x01(\t\x12\x11\n\tplayer_id\x18\x02 \x01(\t\"&\n\x11\x43reateGameRequest\x12\x11\n\tplayer_id\x18\x01 \x01(\t\"\xd0\x01\n\x0fPlayHandRequest\x12\x11\n\tplayer_id\x18\x01 \x01(\t\x12\x0f\n\x07game_id\x18\x02 \x01(\t\x12:\n\tintention\x18\x03 \x01(\x0e\x32\'.grpc.testing.PlayHandRequest.Intention\x12 \n\x04hand\x18\x04 \x01(\x0b\x32\x12.grpc.testing.Hand\";\n\tIntention\x12\x0f\n\x0b\x43LAIM_TRUMP\x10\x00\x12\r\n\tPLAY_HAND\x10\x01\x12\x0e\n\nHIDE_KITTY\x10\x02\":\n\x10PlayHandResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x15\n\rerror_message\x18\x02 \x01(\t\"\xb0\x01\n\x06Player\x12\x11\n\tplayer_id\x18\x01 \x01(\t\x12)\n\rcards_on_hand\x18\x02 \x01(\x0b\x32\x12.grpc.testing.Hand\x12(\n\x0cwinning_pile\x18\x03 \x01(\x0b\x32\x12.grpc.testing.Hand\x12/\n\x13\x63urrent_round_trick\x18\x04 \x01(\x0b\x32\x12.grpc.testing.Hand\x12\r\n\x05score\x18\x05 \x01(\x05\"\xcc\x02\n\x04Game\x12\x0f\n\x07game_id\x18\x01 \x01(\t\x12\x19\n\x11\x63reator_player_id\x18\x02 \x01(\t\x12\x18\n\x10\x64\x65\x61ler_player_id\x18\x03 \x01(\t\x12\x1b\n\x13next_turn_player_id\x18\x04 \x01(\t\x12&\n\x1e\x63urrent_round_winner_player_id\x18\x05 \x01(\t\x12%\n\x07players\x18\x06 \x03(\x0b\x32\x14.grpc.testing.Player\x12!\n\x05kitty\x18\x07 \x01(\x0b\x32\x12.grpc.testing.Hand\x12+\n\ntrump_suit\x18\x08 \x01(\x0e\x32\x17.grpc.testing.Card.Suit\x12)\n\ttrump_num\x18\t \x01(\x0e\x32\x16.grpc.testing.Card.Num\x12\x17\n\x0f\x64\x65\x63k_card_count\x18\n \x01(\x05\"\xdc\x02\n\x04\x43\x61rd\x12%\n\x04suit\x18\x01 \x01(\x0e\x32\x17.grpc.testing.Card.Suit\x12#\n\x03num\x18\x02 \x01(\x0e\x32\x16.grpc.testing.Card.Num\"k\n\x04Suit\x12\x12\n\x0eSUIT_UNDEFINED\x10\x00\x12\n\n\x06HEARTS\x10\x01\x12\n\n\x06SPADES\x10\x02\x12\t\n\x05\x43LUBS\x10\x03\x12\x0c\n\x08\x44IAMONDS\x10\x04\x12\x0f\n\x0bSMALL_JOKER\x10\x05\x12\r\n\tBIG_JOKER\x10\x06\"\x9a\x01\n\x03Num\x12\x11\n\rNUM_UNDEFINED\x10\x00\x12\x07\n\x03\x41\x43\x45\x10\x01\x12\x07\n\x03TWO\x10\x02\x12\t\n\x05THREE\x10\x03\x12\x08\n\x04\x46OUR\x10\x04\x12\x08\n\x04\x46IVE\x10\x05\x12\x07\n\x03SIX\x10\x06\x12\t\n\x05SEVEN\x10\x07\x12\t\n\x05\x45IGHT\x10\x08\x12\x08\n\x04NINE\x10\t\x12\x07\n\x03TEN\x10\n\x12\x08\n\x04JACK\x10\x0b\x12\t\n\x05QUEEN\x10\x0c\x12\x08\n\x04KING\x10\r\")\n\x04Hand\x12!\n\x05\x63\x61rds\x18\x01 \x03(\x0b\x32\x12.grpc.testing.Card2\xae\x02\n\x07Shengji\x12\x41\n\ncreateGame\x12\x1f.grpc.testing.CreateGameRequest\x1a\x12.grpc.testing.Game\x12\x41\n\tenterRoom\x12\x1e.grpc.testing.EnterRoomRequest\x1a\x12.grpc.testing.Game0\x01\x12I\n\x08playHand\x12\x1d.grpc.testing.PlayHandRequest\x1a\x1e.grpc.testing.PlayHandResponse\x12R\n\x0b\x61\x64\x64\x41IPlayer\x12 .grpc.testing.AddAIPlayerRequest\x1a!.grpc.testing.AddAIPlayerResponseb\x06proto3'
)



_PLAYHANDREQUEST_INTENTION = _descriptor.EnumDescriptor(
  name='Intention',
  full_name='grpc.testing.PlayHandRequest.Intention',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='CLAIM_TRUMP', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='PLAY_HAND', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='HIDE_KITTY', index=2, number=2,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=360,
  serialized_end=419,
)
_sym_db.RegisterEnumDescriptor(_PLAYHANDREQUEST_INTENTION)

_CARD_SUIT = _descriptor.EnumDescriptor(
  name='Suit',
  full_name='grpc.testing.Card.Suit',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='SUIT_UNDEFINED', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='HEARTS', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='SPADES', index=2, number=2,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='CLUBS', index=3, number=3,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DIAMONDS', index=4, number=4,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='SMALL_JOKER', index=5, number=5,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='BIG_JOKER', index=6, number=6,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=1080,
  serialized_end=1187,
)
_sym_db.RegisterEnumDescriptor(_CARD_SUIT)

_CARD_NUM = _descriptor.EnumDescriptor(
  name='Num',
  full_name='grpc.testing.Card.Num',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='NUM_UNDEFINED', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='ACE', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='TWO', index=2, number=2,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='THREE', index=3, number=3,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FOUR', index=4, number=4,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FIVE', index=5, number=5,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='SIX', index=6, number=6,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='SEVEN', index=7, number=7,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='EIGHT', index=8, number=8,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='NINE', index=9, number=9,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='TEN', index=10, number=10,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='JACK', index=11, number=11,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='QUEEN', index=12, number=12,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='KING', index=13, number=13,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=1190,
  serialized_end=1344,
)
_sym_db.RegisterEnumDescriptor(_CARD_NUM)


_ADDAIPLAYERREQUEST = _descriptor.Descriptor(
  name='AddAIPlayerRequest',
  full_name='grpc.testing.AddAIPlayerRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='game_id', full_name='grpc.testing.AddAIPlayerRequest.game_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=31,
  serialized_end=68,
)


_ADDAIPLAYERRESPONSE = _descriptor.Descriptor(
  name='AddAIPlayerResponse',
  full_name='grpc.testing.AddAIPlayerResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='player_name', full_name='grpc.testing.AddAIPlayerResponse.player_name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=70,
  serialized_end=112,
)


_ENTERROOMREQUEST = _descriptor.Descriptor(
  name='EnterRoomRequest',
  full_name='grpc.testing.EnterRoomRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='game_id', full_name='grpc.testing.EnterRoomRequest.game_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='player_id', full_name='grpc.testing.EnterRoomRequest.player_id', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=114,
  serialized_end=168,
)


_CREATEGAMEREQUEST = _descriptor.Descriptor(
  name='CreateGameRequest',
  full_name='grpc.testing.CreateGameRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='player_id', full_name='grpc.testing.CreateGameRequest.player_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=170,
  serialized_end=208,
)


_PLAYHANDREQUEST = _descriptor.Descriptor(
  name='PlayHandRequest',
  full_name='grpc.testing.PlayHandRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='player_id', full_name='grpc.testing.PlayHandRequest.player_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='game_id', full_name='grpc.testing.PlayHandRequest.game_id', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='intention', full_name='grpc.testing.PlayHandRequest.intention', index=2,
      number=3, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='hand', full_name='grpc.testing.PlayHandRequest.hand', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _PLAYHANDREQUEST_INTENTION,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=211,
  serialized_end=419,
)


_PLAYHANDRESPONSE = _descriptor.Descriptor(
  name='PlayHandResponse',
  full_name='grpc.testing.PlayHandResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='success', full_name='grpc.testing.PlayHandResponse.success', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='error_message', full_name='grpc.testing.PlayHandResponse.error_message', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=421,
  serialized_end=479,
)


_PLAYER = _descriptor.Descriptor(
  name='Player',
  full_name='grpc.testing.Player',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='player_id', full_name='grpc.testing.Player.player_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='cards_on_hand', full_name='grpc.testing.Player.cards_on_hand', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='winning_pile', full_name='grpc.testing.Player.winning_pile', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='current_round_trick', full_name='grpc.testing.Player.current_round_trick', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='score', full_name='grpc.testing.Player.score', index=4,
      number=5, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=482,
  serialized_end=658,
)


_GAME = _descriptor.Descriptor(
  name='Game',
  full_name='grpc.testing.Game',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='game_id', full_name='grpc.testing.Game.game_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='creator_player_id', full_name='grpc.testing.Game.creator_player_id', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='dealer_player_id', full_name='grpc.testing.Game.dealer_player_id', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='next_turn_player_id', full_name='grpc.testing.Game.next_turn_player_id', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='current_round_winner_player_id', full_name='grpc.testing.Game.current_round_winner_player_id', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='players', full_name='grpc.testing.Game.players', index=5,
      number=6, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='kitty', full_name='grpc.testing.Game.kitty', index=6,
      number=7, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='trump_suit', full_name='grpc.testing.Game.trump_suit', index=7,
      number=8, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='trump_num', full_name='grpc.testing.Game.trump_num', index=8,
      number=9, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='deck_card_count', full_name='grpc.testing.Game.deck_card_count', index=9,
      number=10, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=661,
  serialized_end=993,
)


_CARD = _descriptor.Descriptor(
  name='Card',
  full_name='grpc.testing.Card',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='suit', full_name='grpc.testing.Card.suit', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='num', full_name='grpc.testing.Card.num', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _CARD_SUIT,
    _CARD_NUM,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=996,
  serialized_end=1344,
)


_HAND = _descriptor.Descriptor(
  name='Hand',
  full_name='grpc.testing.Hand',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='cards', full_name='grpc.testing.Hand.cards', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1346,
  serialized_end=1387,
)

_PLAYHANDREQUEST.fields_by_name['intention'].enum_type = _PLAYHANDREQUEST_INTENTION
_PLAYHANDREQUEST.fields_by_name['hand'].message_type = _HAND
_PLAYHANDREQUEST_INTENTION.containing_type = _PLAYHANDREQUEST
_PLAYER.fields_by_name['cards_on_hand'].message_type = _HAND
_PLAYER.fields_by_name['winning_pile'].message_type = _HAND
_PLAYER.fields_by_name['current_round_trick'].message_type = _HAND
_GAME.fields_by_name['players'].message_type = _PLAYER
_GAME.fields_by_name['kitty'].message_type = _HAND
_GAME.fields_by_name['trump_suit'].enum_type = _CARD_SUIT
_GAME.fields_by_name['trump_num'].enum_type = _CARD_NUM
_CARD.fields_by_name['suit'].enum_type = _CARD_SUIT
_CARD.fields_by_name['num'].enum_type = _CARD_NUM
_CARD_SUIT.containing_type = _CARD
_CARD_NUM.containing_type = _CARD
_HAND.fields_by_name['cards'].message_type = _CARD
DESCRIPTOR.message_types_by_name['AddAIPlayerRequest'] = _ADDAIPLAYERREQUEST
DESCRIPTOR.message_types_by_name['AddAIPlayerResponse'] = _ADDAIPLAYERRESPONSE
DESCRIPTOR.message_types_by_name['EnterRoomRequest'] = _ENTERROOMREQUEST
DESCRIPTOR.message_types_by_name['CreateGameRequest'] = _CREATEGAMEREQUEST
DESCRIPTOR.message_types_by_name['PlayHandRequest'] = _PLAYHANDREQUEST
DESCRIPTOR.message_types_by_name['PlayHandResponse'] = _PLAYHANDRESPONSE
DESCRIPTOR.message_types_by_name['Player'] = _PLAYER
DESCRIPTOR.message_types_by_name['Game'] = _GAME
DESCRIPTOR.message_types_by_name['Card'] = _CARD
DESCRIPTOR.message_types_by_name['Hand'] = _HAND
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

AddAIPlayerRequest = _reflection.GeneratedProtocolMessageType('AddAIPlayerRequest', (_message.Message,), {
  'DESCRIPTOR' : _ADDAIPLAYERREQUEST,
  '__module__' : 'shengji_pb2'
  # @@protoc_insertion_point(class_scope:grpc.testing.AddAIPlayerRequest)
  })
_sym_db.RegisterMessage(AddAIPlayerRequest)

AddAIPlayerResponse = _reflection.GeneratedProtocolMessageType('AddAIPlayerResponse', (_message.Message,), {
  'DESCRIPTOR' : _ADDAIPLAYERRESPONSE,
  '__module__' : 'shengji_pb2'
  # @@protoc_insertion_point(class_scope:grpc.testing.AddAIPlayerResponse)
  })
_sym_db.RegisterMessage(AddAIPlayerResponse)

EnterRoomRequest = _reflection.GeneratedProtocolMessageType('EnterRoomRequest', (_message.Message,), {
  'DESCRIPTOR' : _ENTERROOMREQUEST,
  '__module__' : 'shengji_pb2'
  # @@protoc_insertion_point(class_scope:grpc.testing.EnterRoomRequest)
  })
_sym_db.RegisterMessage(EnterRoomRequest)

CreateGameRequest = _reflection.GeneratedProtocolMessageType('CreateGameRequest', (_message.Message,), {
  'DESCRIPTOR' : _CREATEGAMEREQUEST,
  '__module__' : 'shengji_pb2'
  # @@protoc_insertion_point(class_scope:grpc.testing.CreateGameRequest)
  })
_sym_db.RegisterMessage(CreateGameRequest)

PlayHandRequest = _reflection.GeneratedProtocolMessageType('PlayHandRequest', (_message.Message,), {
  'DESCRIPTOR' : _PLAYHANDREQUEST,
  '__module__' : 'shengji_pb2'
  # @@protoc_insertion_point(class_scope:grpc.testing.PlayHandRequest)
  })
_sym_db.RegisterMessage(PlayHandRequest)

PlayHandResponse = _reflection.GeneratedProtocolMessageType('PlayHandResponse', (_message.Message,), {
  'DESCRIPTOR' : _PLAYHANDRESPONSE,
  '__module__' : 'shengji_pb2'
  # @@protoc_insertion_point(class_scope:grpc.testing.PlayHandResponse)
  })
_sym_db.RegisterMessage(PlayHandResponse)

Player = _reflection.GeneratedProtocolMessageType('Player', (_message.Message,), {
  'DESCRIPTOR' : _PLAYER,
  '__module__' : 'shengji_pb2'
  # @@protoc_insertion_point(class_scope:grpc.testing.Player)
  })
_sym_db.RegisterMessage(Player)

Game = _reflection.GeneratedProtocolMessageType('Game', (_message.Message,), {
  'DESCRIPTOR' : _GAME,
  '__module__' : 'shengji_pb2'
  # @@protoc_insertion_point(class_scope:grpc.testing.Game)
  })
_sym_db.RegisterMessage(Game)

Card = _reflection.GeneratedProtocolMessageType('Card', (_message.Message,), {
  'DESCRIPTOR' : _CARD,
  '__module__' : 'shengji_pb2'
  # @@protoc_insertion_point(class_scope:grpc.testing.Card)
  })
_sym_db.RegisterMessage(Card)

Hand = _reflection.GeneratedProtocolMessageType('Hand', (_message.Message,), {
  'DESCRIPTOR' : _HAND,
  '__module__' : 'shengji_pb2'
  # @@protoc_insertion_point(class_scope:grpc.testing.Hand)
  })
_sym_db.RegisterMessage(Hand)



_SHENGJI = _descriptor.ServiceDescriptor(
  name='Shengji',
  full_name='grpc.testing.Shengji',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=1390,
  serialized_end=1692,
  methods=[
  _descriptor.MethodDescriptor(
    name='createGame',
    full_name='grpc.testing.Shengji.createGame',
    index=0,
    containing_service=None,
    input_type=_CREATEGAMEREQUEST,
    output_type=_GAME,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='enterRoom',
    full_name='grpc.testing.Shengji.enterRoom',
    index=1,
    containing_service=None,
    input_type=_ENTERROOMREQUEST,
    output_type=_GAME,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='playHand',
    full_name='grpc.testing.Shengji.playHand',
    index=2,
    containing_service=None,
    input_type=_PLAYHANDREQUEST,
    output_type=_PLAYHANDRESPONSE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='addAIPlayer',
    full_name='grpc.testing.Shengji.addAIPlayer',
    index=3,
    containing_service=None,
    input_type=_ADDAIPLAYERREQUEST,
    output_type=_ADDAIPLAYERRESPONSE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_SHENGJI)

DESCRIPTOR.services_by_name['Shengji'] = _SHENGJI

# @@protoc_insertion_point(module_scope)
