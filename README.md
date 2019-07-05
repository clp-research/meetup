# MeetUp! A Dialogue & Vision Task

MeetUp! is a resource for investigative _visually grounded dialogue_. In the design of the game, we took care that both visual grounding phenomena as well as dialogue phenomena are present. (Unlike some other data resources in this space, which focus more on the visual grounding side.)

MeetUp! is a two-player dialogue coordination game. It is played on a gameboard that can be formalised as a connected subgraph of a two-dimensional grid graph. Players are located at vertices in the graph, which we call "rooms".
Players never see a representation of the whole gameboard, they only see their current room (as an image). They also do not see each other's location.
The images representing rooms are of different types; here, different types of real-world scenes, such as "bathroom", "garage", etc., taken from the ADE20k corpus.
Players can move from room to room, if there is a connecting edge on the gameboard. On entering a room, the player is (privately) informed about the available exit directions as cardinal directions, e.g. "north", "south", etc., and (privately) shown the image that represents the room.
Players move by issuing commands to the game; these are not shown to the other player.

The goal of the players is to be in the same location, which means they also have to be aware of that fact. In the variant explored here, the goal is constrained in advance in that the meetup room has to be of a certain type previously announced to the players; e.g., a kitchen.
The players can communicate via text messages. As they do not see each other's location, they have to describe the images they see to ascertain whether or not they are currently in the same room, and move to a different room if they decide that they aren't. If they have reached the conclusion that they are, they can decide to end the game.

Here is an example of an interaction:

![transcript](transcript.pdf)


How to load the data is described in [the example Jupyter Notebook](examples.ipynb).

If you find the data useful, please cite

> Nikolai Ilinykh, Sina Zarrieß, David Schlangen (2019): Meet Up! A Corpus of Joint Activity Dialogues in a Visual Environment. In *Proceedings of semdial 2019 (LondonLogue)*, London, September 2019

You can find this paper [here](papers/meetup_semdial19.pdf).
