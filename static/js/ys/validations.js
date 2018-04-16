export const titleMaxCharacterCount = 200;

export function validateTitle(title){
  if (!title || title.trim() === '') {
    return "This claim doesn't seem to have any words.";
  } else if (title.length > titleMaxCharacterCount){
    return "This is over the character limit. Try dividing your idea into multiple claims. Remember: brevity is the soul of wit!";
  } else {
    return null;
  }
}
