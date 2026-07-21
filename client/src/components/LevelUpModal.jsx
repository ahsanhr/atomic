export default function LevelUpModal({ isOpen, newLevel, unlockedItem, onClose }) {
  if (!isOpen) return null;

  // figure out what to show for the unlock
  let unlockText;
  if (newLevel === 5) {
    unlockText = "A friend moves in with you!";
  } else if (unlockedItem) {
    unlockText = `You unlocked: ${unlockedItem}!`;
  } else {
    unlockText = "Keep going!";
  }

  return (
    <div className="modalBackground">
      <div className="modalWindow">
        <div className="closeModal">
          <button onClick={onClose}>[ X ]</button>
        </div>
        <p className="eyebrow">Level up!</p>
        <h2 className="header">Level {newLevel}</h2>
        <p>{unlockText}</p>
      </div>
    </div>
  );
}
