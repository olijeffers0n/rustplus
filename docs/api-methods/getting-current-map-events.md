# Getting Current Map Events

The following are all defined as "events":

* Explosions (Bradley / Attack Helicopter)
* Cargo Ship
* CH47 (Chinook)
* Locked Crates
* Attack Helicopter

Calling `rust_socket.get_current_events()` returns a list of all current `RustMarker`'s that are the above events. This can be used for working out whether Cargo Ship / Oil Rig etc has been taken / is being taken. See [Here ](getting-map-markers.md)for information on `RustMarker`

