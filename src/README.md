 # CL match to Wikidata 

 Exploring ways beyond Mix'n'Match to reconcile datasets to Wikidata. 


 Plan: 

 * Create an straightforward cli tool and match CL to Wikidata
   - 1. Generate a Mix'n'Match like sheet. 
   - 2. Set up a JSON with the existing Wikidata matches (local_id : qid) 
   - 3. Set up a curation system to add new matches to this JSON 
   - 4. Upload new matches to Wikidata.

  Maybe turn this into a Flask app, using a small SQL database instead of a JSON and allow web curation. 