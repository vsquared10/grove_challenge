# Instructions

## Activate environment and download necessary files:

From the root directory, execute:
`. venv/bin/activate`

And install the necessary dependencies:
`pip install -r requirements.txt`

## Export the NASA API Key as an environment variable

From bash, run `export NASA_API_KEY=<your_key>`. Running this script without a key will not work. The API can be queried with a sample key, but that sample key is only provided for demonstration purposes and has a unusefully restricted query rate limit.

## Run the script

The script can run with a specified date range or without one. The default values are today as an "end" date and 7 days in the past as a "start" date. It can be run as follows:

`python NEO_pipeline.py <output_filepath> <start_date> <end_date>`

This will generate a .csv file of all "potentially hazardous asteroids" as defined by NASA[https://api.nasa.gov/api.html#NeoWS].

## Additional Notes:

- I've attached relevant screenshots of visualizations that I found useful/interesting, with "NEOs&MileageOverTime.png" being the most relevant to the challenge requirements. 
- I did not complete a proper test suite as I was running short on time. I did, however, spend considerable time & effort testing out different solutions and debugging errors. I recorded a large amount of that effort & exploration in an attached jupyter notebook.
- The instructions had conflicting messages with respect to gathering retroactive vs. prospective data. There was ambiguous language that indicated both. It turns out that the NASA API returns future projections in addition to historical records. I chose future projections as that was the first indication in the instructions, and what I thought would be more interesting to visualize.
- Why 18 years? The API rate limit is 1000 queries per hour, which after some initial testing left me with ~6800 days worth of queries to gather in one solid push. With more time and computing resources (IP masks, etc.) more data could be gathered in a shorter time. The relevant data pull is also included in this repo.
