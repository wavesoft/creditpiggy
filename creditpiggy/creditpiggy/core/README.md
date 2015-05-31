
# Creditpiggy Core App

This Django app implements the core logic of the CreditPiggy application.

## Models

### UserProfile

The user entity in the CreditPiggy project. One or more social profiles can point to one PiggyUser.

Credits and awrards are all coming down to a PiggyUser.


## Housekeeping operations

One of the most important housekeeping operations is to rotate the counter buffers in order to calculate the time series metrics. This is used for collecting the statistical information required for estimating the project's growth and economy.