# How to use Resto-bot

Hi, Resto-bot here 🤖👋! Thanks for giving me a try! I toot 🎺 once a day with a link to a restaurant in OSM that has not been updated in more than 5 years (or, 5 \* 365 days to be exact, but let's not nitpick.) Most restaurants don't exist for that much time, so each restaurant I post deserves a close look!

Here's how I suggest you go about this:

1. Click on the link in my toot. This will take you to the OSM website where the restaurant is already selected.
2. Click "Edit" to go to OSM edit mode. You can use iD (the built in web editor) or JOSM (for nerds 🤓). If you don't have an OSM account yet, you will need to [make one first](https://learnosm.org/en/beginner/start-osm/).
3. Look up the restaurant on the internet. You can use public sources, like the restaurant's own website or social media page, to verify if the restaurant still exists. **Don't use Google Maps or Google Streetview.**
4. If the restaurant is closed, you can delete it. If it is a point (node), you can delete it altogether. Sometimes the restaurant is a building. In that case, you want to leave the building itself, but remove the restaurant-related tags from it.
5. For bonus points, you can add additional information to the restaurant, such as its hours, cuisine, website and phone number. Again, only use their own social media or website. For more bonus points, map some things in the area, such as parking, sidewalks, or trees.
6. Even if everything looks fine, please add a `check_date` tag with the current day as the value, like so: `YYYY-MM-DD`. This lets other mappers know that someone recently checked the information about this restaurant.
7. Upload your changes, please use the hashtag `#restobot`.
8. Respond to the toot with something like "I fixed it!" and a link to your changeset. (If you don't know what that is, just skip it.)
9. Come back tomorrow!

## Things that can go wrong

Lots 🤣. I was created in half a day and I may break or toot incoherent information. Please let [my maintainer](https://vanexel.net/) know.

To know which restaurants to toot about, I took one long look at the OSM database on February 14 ❤️, 2023. Another mapper may have fixed the restaurants I toot about since then, or even deleted them! Best to just ignore me on days when that happens.

If you get stuck and don't know how to fix the restaurant, you can reply to my toots and ask someone else for help, or reach out to [the OSM community](https://community.osm.be/).
