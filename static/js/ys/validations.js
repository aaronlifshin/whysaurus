import validator from 'validator'
export const titleMaxCharacterCount = 200

export function validateTitle(title){
  if (!title || title.trim() === '') {
    // Disabling this warning for now bc our logic for disabling the publish button is taking care of it,
    // and our WIP logic for displaying the feedback area is making this flash in a distracting way -JF
    //   return "This claim doesn't seem to have any words.";
    return ""
  } else if (title.length > titleMaxCharacterCount){
    return "This is over the character limit. Try dividing your idea into multiple claims. Remember: brevity is the soul of wit!";
  } else {
    return null
  }
}

export const captionMaxCharacterCount = 1000

export function validateCaption(caption){
  if (caption && caption.length > titleMaxCharacterCount){
    return "This is over the character limit."
  } else {
    return null
  }
}

export function validateSourceName(name){
  return null
}

export function validateSourceURL(url){
  if (!url) {
    return "URL is required."
  } else if (!validator.isURL(url)) {
    return "This doesn't look a valid URL."
  } else {
    return null;
  }
}
