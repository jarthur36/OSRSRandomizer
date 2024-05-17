from flask import current_app as app, render_template, url_for, request
from .randomiser import roll_crate, all_gear, is_cosmetic, assign_quality, is_pvp_only

@app.route('/')
def home():
    return "Welcome to the randomiser. Visit /roll to roll a crate"

def get_colour_from_quality(quality: float):
    if quality < 0.3:
        return "common"
    elif quality < 0.6:
        return "rare"
    elif quality < 0.8:
        return "epic"
    else:
        return "legendary"

@app.route('/roll')
def roll():
    try:
        n_rolls = int(request.args.get('n_rolls', "9"))
        quality = float(request.args.get('quality', "0.5"))
    except:
        return "Something went wrong, sorry pal!"
    tradable_items = [item for item in all_gear if item.tradeable and not is_cosmetic(item) and not is_pvp_only(item)]
    crate, max_weights  = roll_crate(quality, n_rolls, tradable_items, debug=True)
    
    
    processed_crate = [
        {
            "name": item.name,
            "wiki_url": item.wiki_url,
            "icon": item.icon,
            "quality": assign_quality(item)/max_weights[idx],
            "quality_color": get_colour_from_quality(assign_quality(item)/max_weights[idx]),
            "slot": item.equipment.slot
        }
        for idx, item in enumerate(crate)
    ]
    return render_template('index.html', crate=processed_crate)