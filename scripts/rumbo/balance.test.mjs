// Rumbo's balance: does listening pay? Bots play whole sessions on the real economy and clip bank.
//   blind:  never listens; trades on the stations' base prices (what the blurbs hint at)
//   listen: hears each station's broadcast when it docks and remembers the others' last prices
//   omni:   knows every station's true price now
// The game's premise is that listening is worth a lot more than guessing. Run: node --test scripts/rumbo/
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import * as E from "../../public/rumbo/economy.js";
import { STATION_IDS, GOOD_IDS, fuel, START, SESSION_TURNS } from "../../public/rumbo/data.js";

const bankUrl = new URL("../../media/rumbo/bank.json", import.meta.url);
const bank = fs.existsSync(bankUrl) ? JSON.parse(fs.readFileSync(bankUrl, "utf8")) : null;
const CLIPS = bank ? (bank.clips || bank).filter((c) => !c.bad) : [];
const EVENT_TYPES = [...new Set(CLIPS.filter((c) => c.kind === "rumor").map((c) => c.facts.event))];

export function playBot(seed, mode) {
  const W = E.newWorld(seed, 0, { eventTypes: EVENT_TYPES, turns: SESSION_TURNS });
  const ship = { credits: START.credits, cargo: {}, at: START.station, hold: START.hold };
  const memo = {}, used = new Set();
  const arrive = () => {
    const b = E.pickBroadcast(CLIPS, W, ship.at, used);
    if (b) { E.bindBroadcast(W, ship.at, b.facts.prices); used.add(b.id); }
    memo[ship.at] = E.prices(W, ship.at);
  };
  const known = (st, g) => (mode === "blind" ? E.basePrice(st, g) : mode === "omni" ? E.price(W, st, g) : memo[st]?.[g] ?? E.basePrice(st, g));
  const w0 = E.netWorth(ship, W);
  arrive();
  for (let t = 0; t < SESSION_TURNS - 1; t++) {
    const st = ship.at;
    for (const [g, c] of Object.entries(ship.cargo)) if (c.qty) { ship.credits += E.trade(W, st, g, -c.qty).total; c.qty = 0; }
    let best = null;
    for (const to of STATION_IDS) if (to !== st) for (const g of GOOD_IDS) {
      const buy = known(st, g), n = Math.min(ship.hold, Math.floor(ship.credits / (buy * 1.12)));
      if (n <= 0) continue;
      const gain = E.quote(known(to, g), -n) - E.quote(buy, n) - fuel(st, to);
      if (!best || gain > best.gain) best = { g, to, n, gain };
    }
    let to = STATION_IDS.find((x) => x !== st);
    if (best && best.gain > 0) {
      to = best.to;
      let n = best.n; // the fill is at the true price: buy what the credits cover
      while (n > 0 && E.quote(E.price(W, st, best.g), n) > ship.credits) n--;
      if (n) { ship.credits -= E.trade(W, st, best.g, n).total; ship.cargo[best.g] = { qty: n }; }
    }
    ship.credits -= fuel(st, to); ship.at = to; E.advance(W); arrive();
  }
  return E.netWorth(ship, W) - w0;
}
const median = (a) => [...a].sort((x, y) => x - y)[Math.floor(a.length / 2)];

test("listening pays: hearing the broadcasts beats trading blind by a wide margin", { skip: !bank && "no clip bank" }, () => {
  const seeds = Array.from({ length: 120 }, (_, i) => `bal${i}`);
  const m = Object.fromEntries(["blind", "listen", "omni"].map((k) => [k, median(seeds.map((s) => playBot(s, k)))]));
  assert.ok(m.blind > 0, `blind trading still makes something (${m.blind})`);
  assert.ok(m.listen >= 1.4 * m.blind, `listening ${m.listen} vs blind ${m.blind}`);
  assert.ok(m.omni <= 1.5 * m.listen, `one broadcast a turn is most of what there is to know (${m.omni} vs ${m.listen})`);
});
