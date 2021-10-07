# Early

## About

Automatic profiling of social media users from the analysis of unstructured data.
Early is a Django web application for building datasets, correcting data and validating data from the automatic profiling of social media users from the analysis of unstructured data. 
It also allows you to visualize social media profiles, with the predicted demographic data and the automatically filled Beck Depression Inventory.

## Documentation

- [Thesis documentation](https://github.com/palomapiot/early/blob/develop/_TFM__Memoria.pdf)
- [Gender classification paper](https://github.com/palomapiot/early/blob/develop/Paper.pdf)

## Features

- Create datasets:
  - Source data: Reddit
  - Configure the experiments by subreddit, number of users, number of comments per user, etc.
  - Profile retrieved data by consuming [Profiling Buddy API](https://github.com/palomapiot/profiler-buddy)
- Create corpus to classify the datasets
- Export data:
  - Demographic data
  - Dataset
  - Labeled dataset
  - JSON or CSV format
- Profile user by Reddit username
- View profiles list
- Search and filter profiles
- View profile detail
- Edit and validate profile
- Correct Beck Depression Inventory questionnaire

## API

Check the [OpenAPI specification](https://github.com/palomapiot/early/blob/develop/app/openapi-schema.yml) for more information regarding the API.

## Prerequisites

Run as a container with:

- Docker
- docker-compose

## Installation

Clone the project, install docker and start the service with `docker-compose up`

## Roadmap

- Retrieve data from Twitter
- Improve search engine
- Manage user groups (a user group can access a subset of profiles, not all profiles)
- Add statistics and data visualization of the demographic data of the profiles
- i18n, right now only available in English and Spanish

## Useful links

- [Google developer group](https://groups.google.com/u/1/g/early-dev)
- [Profiler Buddy](https://github.com/palomapiot/profiler-buddy)
- [Web App (staging)](https://earlydetection-staging.herokuapp.com/) 
- [Gender classification paper](https://github.com/palomapiot/early/blob/develop/Paper.pdf)

## License

GNU GPLv3.0
