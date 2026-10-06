/**
 * YoutuberCard — a channel recommendation on the guides pages.
 *
 * Server component; it is a link with a picture.
 */
export interface YoutuberCardProps {
  coverImg: string;
  profileImg: string;
  name: string;
  channelLink: string;
}

export function YoutuberCard({
  coverImg,
  profileImg,
  name,
  channelLink,
}: YoutuberCardProps) {
  return (
    <div className="yt-card">
      <div className="yt-card-image">
        {/* Plain <img>: these are remote channel art at whatever size YouTube
            serves, and next/image would need every host allow-listed. */}
        <img src={coverImg} alt={`${name} channel cover image`} />
      </div>
      <div className="yt-profile-image">
        <img src={profileImg} alt={`${name} profile picture`} />
      </div>
      <div className="yt-card-content">
        <h3>{name}</h3>
        <a
          className="yt-subscribe"
          target="_blank"
          rel="noopener noreferrer"
          href={channelLink}
        >
          <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path d="M23.5 6.2a3 3 0 0 0-2.1-2.1C19.5 3.5 12 3.5 12 3.5s-7.5 0-9.4.6A3 3 0 0 0 .5 6.2 31.3 31.3 0 0 0 0 12a31.3 31.3 0 0 0 .5 5.8 3 3 0 0 0 2.1 2.1c1.9.6 9.4.6 9.4.6s7.5 0 9.4-.6a3 3 0 0 0 2.1-2.1A31.3 31.3 0 0 0 24 12a31.3 31.3 0 0 0-.5-5.8zM9.6 15.6V8.4l6.2 3.6-6.2 3.6z" />
          </svg>
          Subscribe
        </a>
      </div>
    </div>
  );
}

export default YoutuberCard;
