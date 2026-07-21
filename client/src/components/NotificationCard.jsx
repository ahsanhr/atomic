export default function NotificationCard({ notification }) {
  return (
    <article className="notification-card">
      <h3>{notification.title}</h3>
      <p>{notification.message}</p>
    </article>
  );
}