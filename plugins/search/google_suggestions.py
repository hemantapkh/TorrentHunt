from pyrogram import Client, filters, types


@Client.on_inline_query(filters.regex('!google'))
async def google_suggestions(Client, inline_query):
    query_list = inline_query.query.split()
    results = []

    # If keyword is not empty
    if len(query_list) > 1:
        keyword = ' '.join(query_list[1:])
        suggestions = await Client.MISC.google_suggestions(keyword)
        if suggestions:
            pm_text = f'Google result for "{keyword}"'
            for suggestion in suggestions:
                results.append(
                    types.InlineQueryResultArticle(
                        title=suggestion,
                        input_message_content=types.InputTextMessageContent(
                            message_text=suggestion,
                        ),
                    ),
                )

        # No suggestions found
        else:
            pm_text = 'No result found'

    # If keyword is empty
    else:
        pm_text = 'Enter a keyword to search'

    await Client.answer_inline_query(
        inline_query.id,
        results=results,
        cache_time=10,
        switch_pm_text=pm_text,
        switch_pm_parameter='inlineQuery',
    )
