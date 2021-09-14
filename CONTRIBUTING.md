Contributing to Decision Maximizer 3000 (DM3K)
=========

DM3K encourages community extensions and improvements.  We currently have a core team of 1, and I have limited time to maintain or actively develop, so please be patient with any requests or issues.  

Given that, the contribution process is less formal than for larger projects, but please follow the usual:
1. Clone the project.  (optional: look through existing issues)
2.  Follow the [*/docs/dev_env.md*](/docs/dev_env.md) instructions to set up your environment.
3. Create a new branch. <br>
 If you are making substantial changes, please create an issue first.  You can then name your branch `<issue #>-<description-of-feature>`
4. Commit your changes  
5. Create new unit tests for your functionality, and check that tests pass: `docker exec -ti dm3k_api python -m unittest discover -v -s /app/tests`
6. Push to that branch
7. Create a new Merge Request in GitHub

__Thank you for your contribution!__ Your help is very much appreciated.