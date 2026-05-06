# Continual data cleaning activities
- Investigate null or OTHER values in the data from site_data.json and see how they can be removed by adding more categories in our schema. Done on 2026-05-04.

# To implement / brainstorm

- [ ] No deaths or their details are shown in any page at all, *except* for accumulated statistics; you can see the number of deaths in all the works of an author, but you can't see the number of deaths in a particular book, game, movie, episode, short story, or any other pieces of media. *except* when...
- [ ] You mark a piece of media as "completed". This is not stored in the database but as cookies in the user's browser. On the navbar there could be a button, uh, "Mark as completed" or something. when you click on it you're given an in-html popup where you can type the names of medias, they even appear underneath as you type so you can select them quicker. When you type in a show, it gives a warning "Marking a show as read will mark all episodes as read as well." A similar warning for authors is also given. There's also a Mnesia mode, where nothing at all is hidden ever.
- [ ] Pages for each method of killing: with the pieces of media it is in collapsed because of the spoiler heavy nature unless you have marked them as read, but visible when you click over them.
- [ ] Remove all pages in the navbar actually. Have this: Deaths | Methods | People | Media. on the people page you can filter by victims, detectives, solvers, or killers.
- [ ] Show author statistics for each author page.
- [ ] Have new pages for each method of killing that show statistics about that method.
- [ ] Subcategories for each method of killing: like poisoning should connect to a poisons db, shot should connect to a guns db etc.
- [ ] Get a list of all TV tropes articles relating to murders and mysteries and murder mysters, then somehow link them to the relevant media.
- [ ] For global data use statistics for how many deaths are caused by each method of killing.

## Visualisation ideas
- Pie charts or iconography (like icons for each method of killing and an entire table of those icons, where each element is 1 or x deaths etc.) to represent how many people die by what.
- Database of Poisons.
- Database of ways of faking alibis, faking 1 of the 5 locked room axioms etc.

# Media to add
- [ ] All Columbo episodes.
- [ ] All The Mentalist episodes.
- [ ] All Psyche episodes.
- [ ] All Psyche movies.
- [ ] All Sherlock Holmes books.
- [ ] All the novels of all Golden Age crime fiction authors, which includes...
- [ ] John Dickson Carr books. Will have to figure out how to handle locked rooms before this.
- [ ] All detective fiction by GK Chesterton.
