---
description: Learn more about command customizations
---

# Commands Settings

<details>

<summary>Adventure</summary>

### Available Adventures

These adventures are currently implemented in Dank Memer Grinder:

* [x] Space
* [x] Pasture (Out West)
* [ ] Trick or Treating
* [ ] Winter Wonderland
* [ ] Museum
* [x] Brazil
* [x] Vacation

To choose an adventure, find the "Adventure" drop down menu in the Settings tab and select the adventure you want the Dank Memer Grinder to run.

### Adventure Answers

Dank Memer Grinder allows you to optimize your adventure success rate or profits by customizing the answers it chooses. You can configure different responses in the `config.json` file. [Dank Memer Adventure Guides](https://docs.google.com/spreadsheets/d/14AC-mmYNMrcdDGxfG2Nv0OAwq-Pkth1SIJuW3ADSXYQ/edit#gid=1274532499) is a useful tool for choosing answers.

#### Answer Format

The format for specifying adventure answers is:

```json
"question": "answer button name"
```

Where `question` is the text of the prompt, and `answer button name` is the label of the button to click in response.

### Default Adventure Answers

{% code title="config.json" %}
```json
"adventure": {
    "brazil": {
        "After a long day shopping for souvenirs in a crowded mall, you stop at the food court to grab some food. What do you order?": "McDonald's",
        "On your way to the beach, you stop at a comer store to buy some drinks and notice a litle caramel-colored dog is sleeping outside. What do you do?": "Pet the Dog",
        "While enjoying Carnival, you decide to go to the stadium to watch the samba schools perform. Where do you buy your tickets?": "Online",
        "While traveling in the city, you hear about Snake Island and decide you have to see if it is really as bad as they say. The boat captain will take you there but demands more money if you want to dock. What do you do?": "Stay on the Boat",
        "While visiting Rio Grande do Sul, you stop at one of the famous Brazilian steakhouses with all the meat you can eat. What do you want?": "Broccoli",
        "While visiting S�o Paulo, you find a place to see capybaras. What do you do?": "Pull up",
        "You can't get enough of the Brazilian beaches, and decide to spend the day exploring a remote one you found. What do you do first?": "Go Swimming",
        "You can't visit Rio de Janeiro without touring the Christ the Redeemer statue. How do you get there?": "Bus",
        "You decide to take an MMA class while visiting to learn from the best. Which style do you choose?": "Capoiera",
        "You stop at a local bakery for some of the Brazilian cheese bread you've heard so much about. What else do you try?": "Nothing",
        "You take a boat tour in Manaus to go down the Amazon River. At a fork in the path, the guide tells you to the right are piranhas and left anacondas. Which do you choose?": "Piranhas",
        "You went to schedule a trip into the Amazon to see the animals. What sort of trip do you book?": "Private Tour"
    },
    "space": {
        "A friendly alien approached you slowly. What do you do?": "Attack",
        "A small but wise green alien approaches you.": "Do",
        "Oh my god even in space you cannot escape it": "69",
        "This planet seems to be giving off radioactive chemicals. What do you do?": "Distant Scan",
        "Whaaaat!? You found a space kitchen! It looks like it is full of shady stuff. What do you do?": "Inspect",
        "You accidentally bumped into the Webb Telescope. Oh god.": "Flee",
        "You come upon a dark pyramid shaped ship fighting a spherical white ball looking thing. What do you do?": "Embrace Dark",
        "You encountered someone named Dank Sidious, what do you do?": "Do it",
        "You find a vending machine selling \"Moon Pies\". What do you do?": "Buy",
        "You flew past a dying star": "Flee",
        "You found a strange looking object. What do you do?": "Ignore",
        "You got abducted by a group of aliens, who are trying to probe you. What do you do?": "Sit Back and Enjoy",
        "You ran out of fuel! What next?": "Urinate",
        "You see a shooting star!": "Wish",
        "You uh, just came across a pair of Odd Eyes floating around": "Flee",
        "You're picking up a transmission from deep space!": "*<)#%':]|##"
    },
    "vacation": {
        "A family road trip is a perfect getaway until you end up lost and without cell service. What do you do?": "Keep Driving",
        "A family vacation can't be complete without a trip to an amusement park. What ride are you dying to try?": "Waterslide",
        "A friend tells you about a quaint mountain resort, so you decide to spend a few days enjoying the snow. What do you do after you arrive?": "Go Skiing",
        "Camping has always relaxed you, so you decide to vacation in the wilderness. What sort of camping do you prefer?": "Rent an RV",
        "During your vacation in Lisbon, the hotel offers you a small pastry for breakfast. What do you do?": "Pass",
        "Nothing can beat a romantic vacation in Paris. What do you want to do first?": "Louvre",
        "You can't go on vacation without doing a little sightseeing. What do you want to see?": "Museum",
        "You decide it's time to visit some famous landmarks in the United States. Which do you visit first?": "Mt. Rushmore",
        "You decide the beach sounds like a perfect choice for a weekend away. Which beach do you want to visit?": "Daytona Beach, Florida",
        "You decide to go stargazing in the Chilean desert, but there are only two flights left. Which do you take?": "Night",
        "You decide to pick up Badosz and spend the weekend at Legoland. What do you look at first?": "Gift Shop",
        "You find a discounted whale watching tour and decide to give it a go, but the deal is for two. Who do you take with you?": "Kable",
        "You get a flyer for some discount cruises that sound wonderful. Which destination do you choose?": "Mediterranean",
        "Your cruise ship docks at a small island for a day of sun and swimming. What do you do?": "Sunbathe",
        "While vacationing in Rome, you visit the Colosseum and run into a group of people handing out friendship bracelets. What do you do?": "Take a Bracelet"
    },
    "west": {
        "A lady next to a broken down wagon is yelling for help.": "Ignore Her",
        "A snake is blocking your path. What do you want to do?": "Wait",
        "A stranger challenges you to a quick draw. What do you want to do?": "Decline",
        "Someone is getting ambushed by bandits!": "Ignore them",
        "Someone on the trail is lost and asks you for directions.": "Ignore them",
        "You bump into someone near the horse stables. They challenge you to a duel": "Run away",
        "You come across a saloon with a poker game going on inside. What do you want to do?": "Join",
        "You entered the saloon to rest from the journey. What do you want to do?": "Play the piano",
        "You find a dank cellar with an old wooden box": "Ignore it",
        "You find an abandoned mine. What do you want to do?": "Explore",
        "You found a stray horse. What do you want to do?": "Feed",
        "You get on a train and some bandits decide to rob the train. What do you do?": "Don't hurt me!",
        "You see some bandits about to rob the local towns bank. What do you do?": "Stop them",
        "You wander towards an old abandoned mine.": "Go in",
        "You're dying of thirst. Where do you want to get water?": "Cactus",
        "You're riding on your horse and you get ambushed. What do you do?": "Run away",
        "Your horse sees a snake and throws you off. What do you do?": "Find a new horse",
        "Who will you take down?": "Billy Bob Jr."
    }
}
```
{% endcode %}

</details>

<details>

<summary>Search</summary>

### Search Priorities

You can configure your search priorities by editing the `config.json` file. This allows you to specify preferred and avoided locations to search.

* The **"priority"** array determines the top search locations. Locations in this array will be checked first when searching.
* The **"second\_priority"** array specifies secondary search locations that will be checked after the top priorities.
* The **"avoid"** array lists locations that should be avoided during searches. If no priority locations are found, searches will avoid locations in these arrays.

#### Default Search Priorities

<pre class="language-json" data-title="config.json"><code class="lang-json"><strong>"priority": [
</strong>    "phoenix pits",
    "aeradella's home",
    "shadow's realm",
    "dog",
    "grass",
    "air",
    "kitchen",
    "dresser",
    "mail box",
    "bed",
    "couch",
    "pocket",
    "toilet",
    "washer",
    "who asked"
],
"second_priority": ["fridge", "twitter", "vacuum"]
"avoid": [
    "bank",
    "discord",
    "immortals dimension",
    "laundromat",
    "soul's chamber",
    "police officer",
    "tesla",
    "supreme court"
]
</code></pre>

</details>

<details>

<summary>Crime</summary>

### Crime Priorities

You can configure your crime priorities by editing the `config.json` file. This allows you to specify preferred and avoided locations for crime.

* The **"priority"** array determines the top crime locations. Locations in this array will be checked first when searching.

<!---->

* The **"second\_priority"** array specifies secondary crime locations that will be checked after the top priorities.

<!---->

* The **"avoid"** array lists locations that should be avoided during crimes. If no priority locations are found, crimes will avoid locations in these arrays.

<pre class="language-json" data-title="config.json"><code class="lang-json"><strong>"priority": [
</strong>    "hacking",
    "tax evasion",
    "fraud",
    "eating a hot dog sideways",
    "trespassing"
],
"second_priority": [
    "fridge", 
    "twitter", 
    "vacuum"
],
"avoid": [
    "bank",
    "discord",
    "immortals dimension",
    "laundromat",
    "soul's chamber",
    "police officer",
    "tesla",
    "supreme court"
]
</code></pre>

</details>

<details>

<summary>Trivia</summary>

### Trivia Correct Chance

The Trivia Correct Chance setting in Dank Memer Grinder's Settings tab lets you adjust the percentage of correct trivia answers from 1-100%.  Higher percentages mean more accurate trivia responses, the default accuracy 75%.

</details>

<details>

<summary>Stream</summary>

### Streaming Order

Dank Memer Grinder allows you to configure the order in which it interacts with a stream. This allows you to prioritize gaining Levels or earning profits.

* 0: Run AD (Moderate chance of failing)
* 1: Read Chat (Low chance of failing)
* 2: Collect Donations (High chance of failing)

### Default Streaming Order

{% code title="captcha.json" %}
```json
"order": [1, 1, 1, 1, 1, 0, 0, 0, 2, 2, 2]
```
{% endcode %}

</details>
