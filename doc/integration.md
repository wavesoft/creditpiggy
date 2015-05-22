# Integration Notes

This document can help you integrate `CreditPiggy` in your own project. The project itself supports various different APIs

## Points of integration

You __MUST__ include some code in two locations in your job management framework:

 1. _Job Agent_: Include user token with the job results
 2. _Job Reception_: Give credits to the user

And you __MAY__ want to include some additional logic in the job agent in order to export run-time information in a machine-readable format, that would be later presented to the user.

## API Flavours

Depending on your project implementation, `CreditPiggy` offers a variety of different API flavours. You can get:

 * `text` - For plaintext requests and responses (ex. with bash scripts)
 * `json` - For JSON I/O
 * `jsonp` - For use in javascript projects
