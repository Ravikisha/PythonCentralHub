/**
 * BuyMeCoffee — the support link.
 *
 * Server component. The cup is a static inline SVG, converted from the Astro
 * original mechanically (attributes camelCased for JSX) rather than retyped,
 * so no path data was touched.
 */
export interface BuyMeCoffeeProps {
  /** Extra class names for the wrapper. */
  class?: string;
}

export function BuyMeCoffee({ class: extraClass = "" }: BuyMeCoffeeProps) {
  return (
    <div className={`bmc-wrapper ${extraClass}`.trim()}>
      <p className="bmc-tagline">Enjoying the site?</p>
      <a
        href="https://buymeacoffee.com/ravikisha"
        target="_blank"
        rel="noopener noreferrer"
        className="bmc-btn"
        aria-label="Buy me a coffee"
      >
        <svg
          className="bmc-icon"
          viewBox="0 0 884 1279"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          aria-hidden="true"
        >
          {/*Cup*/}
          <path
            d="M791.109 297.518L790.231 297.002L788.201 296.383C789.018 297.072 790.04 297.472 791.109 297.518Z"
            fill="#0D0C22"
          />
          <path
            d="M803.896 388.891L802.916 389.166L803.896 388.891Z"
            fill="#0D0C22"
          />
          <path
            d="M791.484 297.377C791.359 297.361 791.237 297.332 791.118 297.29C791.205 297.369 791.319 297.414 791.439 297.418L791.484 297.377Z"
            fill="#0D0C22"
          />
          <path
            d="M791.5 297.418C791.36 297.466 791.21 297.481 791.063 297.461C791.216 297.514 791.384 297.506 791.532 297.436L791.5 297.418Z"
            fill="#0D0C22"
          />
          <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M700.968 145.304C781.928 178.927 843.124 244.261 875.4 331.206C905.321 413.719 905.03 509.031 875.176 591.279C843.9 677.141 781.369 741.821 700.979 775.386C664.615 790.939 626.454 798.919 588.294 799.104L480.568 900.137L480.499 900.068L479.688 899.324L349.24 1015.73H347.397L193.222 1015.73C185.102 1015.73 178.529 1009.28 178.529 1001.28V803.702H193.222H347.397L349.24 803.69L418.875 869.95L478.845 813.463L479.628 812.693L479.697 812.762L481.497 811.114L481.566 811.183L588.294 712.434C626.455 712.619 664.616 720.599 700.979 736.152C690.682 712.034 684.822 686.007 684.055 659.362C683.288 632.718 687.622 606.321 697.137 581.916C739.868 472.469 739.868 339.456 697.137 230.009C684.534 197.549 667.364 168.286 646.578 143.027C665.019 141.819 683.304 143.075 700.968 145.304Z"
            fill="#FFDD00"
          />
          <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M275.57 895.79L346.397 830.615H192.222V1001.28C192.222 1002.06 192.354 1002.8 192.594 1003.49L275.57 895.79Z"
            fill="#0D0C22"
          />
          <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M479.688 899.324L480.499 900.068L480.568 900.137L588.294 799.104C568.585 799.201 548.876 797.093 529.548 792.85L479.688 899.324Z"
            fill="#0D0C22"
          />
          <path
            d="M788.201 296.383L790.231 297.002L791.109 297.518C790.286 296.948 789.281 296.611 788.201 296.383Z"
            fill="#0D0C22"
          />
          <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M609.048 151.651C602.978 165.703 598.302 180.526 595.137 195.95L474.365 75.4444L477.603 72.2486L609.048 151.651Z"
            fill="#0D0C22"
          />
          <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M609.048 151.651L477.603 72.2486L474.365 75.4444L595.137 195.95C598.302 180.526 602.978 165.703 609.048 151.651Z"
            fill="white"
            fill-opacity="0.4"
          />
          <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M478.845 813.463L418.875 869.95L349.24 803.69L275.57 895.79L192.594 1003.49C193.484 1005.99 195.678 1007.87 198.369 1008.45L347.397 1015.73H349.24L479.688 899.324L529.548 792.85C512.846 789.064 496.594 783.686 480.999 777.002L478.845 813.463Z"
            fill="#0D0C22"
          />
          <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M418.875 869.95L349.24 803.69V803.702H347.397L193.222 803.702H178.529V1001.28C178.529 1009.28 185.102 1015.73 193.222 1015.73H347.397L349.24 1015.73L479.688 899.324L480.499 900.068L480.568 900.137L529.548 792.85C512.846 789.064 496.594 783.686 480.999 777.002L478.845 813.463L418.875 869.95Z"
            fill="#FFDD00"
          />
          <path
            d="M164 599.5H572"
            stroke="#0D0C22"
            strokeWidth="40"
            strokeLinecap="round"
          />
          {/*Steam lines*/}
          <path
            d="M202 158C202 158 170 214 202 261C234 308 202 358 202 358"
            stroke="#0D0C22"
            strokeWidth="22"
            strokeLinecap="round"
          />
          <path
            d="M372 158C372 158 340 214 372 261C404 308 372 358 372 358"
            stroke="#0D0C22"
            strokeWidth="22"
            strokeLinecap="round"
          />
          <path
            d="M287 96C287 96 255 152 287 199C319 246 287 296 287 296"
            stroke="#0D0C22"
            strokeWidth="22"
            strokeLinecap="round"
          />
          {/*Cup body*/}
          <path
            d="M146 420H590L556 750H180L146 420Z"
            fill="#FFDD00"
            stroke="#0D0C22"
            strokeWidth="22"
          />
        </svg>
        <span>Buy me a coffee</span>
      </a>
    </div>
  );
}

export default BuyMeCoffee;
