# p22-41
myPAD web app

* User logs in
* Email of user captured and used to get their RESNO
* Supervisees are determined using user RESNO
* Evaluation of user if supervisor depends on supervisees returned
    - 0 supervisees -> non-supervisor
    - 1 or more supervisees -> supervisor<sup>1
* Non-supervisees redirected to non-supervisor page
* Supervisors redirected to index page

\
When supervisees are found<sup>1<br>

* Supervisees taken from OCS using supervisor RESNO as XML
* XML converted to dictionary
* Supervisees list created from dictionary and rendered in index page showing the following:
  * Smiley
  * Name
  * RESNO
  * Link to supervisee myPAD
  * Rating date
  * Rating button<sup>2<br>
* A session supervisee dataset is created and stored to a variable
* The variable containing the supervisee dataset is modified after each rating and used for subsequent index rendering

\
When rating button is clicked<sup>2

* When rating button is clicked, user is redirected to ratestaff page
* A confirmation modal is shown when a rating is made
* If rating is confirmed, rating and rating date is written to OCS
* Supervisee data is reloaded to reflect latest changes
* User is redirected to index page containing latest supervisee data

## On deploying a stage using Zappa
Make sure to do the following prior to calling zappa deploy command for a newly-opened terminal session:
```
export AWS_PROFILE=<your AWS profile for that stage>
```

then
```
aws sso login
```

## Development issues tracker
** First three numbers: Issue tag number. Last two numbers: Resolved flag, 00 - unresolved 01 - resolved
* [001-00] : Rating of previous staff rated reverts to previous rating after another staff is rated\
[Solution-001] : Session supervisee data reassigned with modified supervisee session data after rating


* [002-00] : Session data of supervisees not updated after rating. Loads previous rating when another staff is rated.\
[Solution-002] : Re-initialized session data by itself


* [003-00] : Async processing of patch rating request\
[Solution-003] : Using Zappa Async task in patch code


* [004-00] : Disable Rate button of probationary staff\
[Solution-004] : If statement evaluating remark attribute


* [005-00] : Add myPAD year to title of app\
[Solution-005] : Added to session data on splash screen


* [006-00] : Error handling\
[Solution-006] : Resolved by modifying error handling code for 500 and 404


* [007-00] : Modified help\
[Solution-007] : Created help route for dedicated help page


* [008-00] : Move help button to allot more space for name of user\
[Solution-008] : Moved help button back button to nav bar. Back button z-index set to 9999 to cover help button


* [009-00] : Splash screen background not full height on mobile.\
[Solution-009] : Set vh and width of background image. Changed background image.


* [010-00] : Help button showing in non-supervisor access page\
[Solution-010] : Overlap div with z-index 99999 to cover help button