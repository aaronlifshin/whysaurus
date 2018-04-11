export const titleMaxCharacterCount = 200;

export function validateTitle(title){
  if (!title || title.trim() === '') {
    return "This claim doesn't seem to have any words.";
  } else if (title.length > titleMaxCharacterCount){
    return "You're over the character limit. Try dividing this idea into multiple claims.";
  } else {
    return null;
  }
}
