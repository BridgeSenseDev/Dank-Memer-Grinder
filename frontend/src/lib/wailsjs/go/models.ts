export namespace config {
	
	export class AccountsConfig {
	    token: string;
	    channelID: string;
	    state: boolean;
	
	    static createFrom(source: any = {}) {
	        return new AccountsConfig(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.token = source["token"];
	        this.channelID = source["channelID"];
	        this.state = source["state"];
	    }
	}
	export class AdventureCommandConfig {
	    state: boolean;
	    delay: number;
	    adventureOption: string;
	
	    static createFrom(source: any = {}) {
	        return new AdventureCommandConfig(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.state = source["state"];
	        this.delay = source["delay"];
	        this.adventureOption = source["adventureOption"];
	    }
	}
	export class AdventureConfig {
	    space: {[key: string]: string};
	    west: {[key: string]: string};
	    brazil: {[key: string]: string};
	    vacation: {[key: string]: string};
	
	    static createFrom(source: any = {}) {
	        return new AdventureConfig(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.space = source["space"];
	        this.west = source["west"];
	        this.brazil = source["brazil"];
	        this.vacation = source["vacation"];
	    }
	}
	export class GeneralAutobuyConfig {
	    state: boolean;
	    amount: number;
	
	    static createFrom(source: any = {}) {
	        return new GeneralAutobuyConfig(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.state = source["state"];
	        this.amount = source["amount"];
	    }
	}
	export class AutoBuyConfig {
	    huntingRifle: GeneralAutobuyConfig;
	    shovel: GeneralAutobuyConfig;
	    lifeSavers: GeneralAutobuyConfig;
	
	    static createFrom(source: any = {}) {
	        return new AutoBuyConfig(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.huntingRifle = this.convertValues(source["huntingRifle"], GeneralAutobuyConfig);
	        this.shovel = this.convertValues(source["shovel"], GeneralAutobuyConfig);
	        this.lifeSavers = this.convertValues(source["lifeSavers"], GeneralAutobuyConfig);
	    }
	
		convertValues(a: any, classs: any, asMap: boolean = false): any {
		    if (!a) {
		        return a;
		    }
		    if (a.slice && a.map) {
		        return (a as any[]).map(elem => this.convertValues(elem, classs));
		    } else if ("object" === typeof a) {
		        if (asMap) {
		            for (const key of Object.keys(a)) {
		                a[key] = new classs(a[key]);
		            }
		            return a;
		        }
		        return new classs(a);
		    }
		    return a;
		}
	}
	export class GeneralAutoUseConfig {
	    state: boolean;
	
	    static createFrom(source: any = {}) {
	        return new GeneralAutoUseConfig(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.state = source["state"];
	    }
	}
	export class AutoUseConfig {
	    apple: GeneralAutoUseConfig;
	    pizzaSlice: GeneralAutoUseConfig;
	
	    static createFrom(source: any = {}) {
	        return new AutoUseConfig(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.apple = this.convertValues(source["apple"], GeneralAutoUseConfig);
	        this.pizzaSlice = this.convertValues(source["pizzaSlice"], GeneralAutoUseConfig);
	    }
	
		convertValues(a: any, classs: any, asMap: boolean = false): any {
		    if (!a) {
		        return a;
		    }
		    if (a.slice && a.map) {
		        return (a as any[]).map(elem => this.convertValues(elem, classs));
		    } else if ("object" === typeof a) {
		        if (asMap) {
		            for (const key of Object.keys(a)) {
		                a[key] = new classs(a[key]);
		            }
		            return a;
		        }
		        return new classs(a);
		    }
		    return a;
		}
	}
	export class BlackjackCommandConfig {
	    state: boolean;
	    delay: number;
	    amount: string;
	    manuallyRunCommands: boolean;
	
	    static createFrom(source: any = {}) {
	        return new BlackjackCommandConfig(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.state = source["state"];
	        this.delay = source["delay"];
	        this.amount = source["amount"];
	        this.manuallyRunCommands = source["manuallyRunCommands"];
	    }
	}
	export class WorkCommandConfig {
	    state: boolean;
	    delay: number;
	    autoWorkApply: boolean;
	
	    static createFrom(source: any = {}) {
	        return new WorkCommandConfig(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.state = source["state"];
	        this.delay = source["delay"];
	        this.autoWorkApply = source["autoWorkApply"];
	    }
	}
	export class TriviaCommandConfig {
	    state: boolean;
	    delay: number;
	    triviaCorrectChance: number;
	
	    static createFrom(source: any = {}) {
	        return new TriviaCommandConfig(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.state = source["state"];
	        this.delay = source["delay"];
	        this.triviaCorrectChance = source["triviaCorrectChance"];
	    }
	}
	export class StreamCommandConfig {
	    state: boolean;
	    delay: number;
	    order: number[];
	
	    static createFrom(source: any = {}) {
	        return new StreamCommandConfig(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.state = source["state"];
	        this.delay = source["delay"];
	        this.order = source["order"];
	    }
	}
	export class SearchCommandConfig {
	    state: boolean;
	    delay: number;
	    priority: string[];
	    secondPriority: string[];
	    avoid: string[];
	
	    static createFrom(source: any = {}) {
	        return new SearchCommandConfig(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.state = source["state"];
	        this.delay = source["delay"];
	        this.priority = source["priority"];
	        this.secondPriority = source["secondPriority"];
	        this.avoid = source["avoid"];
	    }
	}
	export class PostMemesCommandConfig {
	    state: boolean;
	    delay: number;
	    platform: number[];
	
	    static createFrom(source: any = {}) {
	        return new PostMemesCommandConfig(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.state = source["state"];
	        this.delay = source["delay"];
	        this.platform = source["platform"];
	    }
	}
	export class CrimeCommandConfig {
	    state: boolean;
	    delay: number;
	    priority: string[];
	    secondPriority: string[];
	    avoid: string[];
	
	    static createFrom(source: any = {}) {
	        return new CrimeCommandConfig(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.state = source["state"];
	        this.delay = source["delay"];
	        this.priority = source["priority"];
	        this.secondPriority = source["secondPriority"];
	        this.avoid = source["avoid"];
	    }
	}
	export class GeneralCommandConfig {
	    state: boolean;
	    delay: number;
	
	    static createFrom(source: any = {}) {
	        return new GeneralCommandConfig(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.state = source["state"];
	        this.delay = source["delay"];
	    }
	}
	export class CommandsConfig {
	    adventure: AdventureCommandConfig;
	    beg: GeneralCommandConfig;
	    blackjack: BlackjackCommandConfig;
	    crime: CrimeCommandConfig;
	    daily: GeneralCommandConfig;
	    deposit: GeneralCommandConfig;
	    dig: GeneralCommandConfig;
	    highlow: GeneralCommandConfig;
	    hunt: GeneralCommandConfig;
	    pets: GeneralCommandConfig;
	    postmemes: PostMemesCommandConfig;
	    scratch: GeneralCommandConfig;
	    search: SearchCommandConfig;
	    stream: StreamCommandConfig;
	    trivia: TriviaCommandConfig;
	    work: WorkCommandConfig;
	
	    static createFrom(source: any = {}) {
	        return new CommandsConfig(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.adventure = this.convertValues(source["adventure"], AdventureCommandConfig);
	        this.beg = this.convertValues(source["beg"], GeneralCommandConfig);
	        this.blackjack = this.convertValues(source["blackjack"], BlackjackCommandConfig);
	        this.crime = this.convertValues(source["crime"], CrimeCommandConfig);
	        this.daily = this.convertValues(source["daily"], GeneralCommandConfig);
	        this.deposit = this.convertValues(source["deposit"], GeneralCommandConfig);
	        this.dig = this.convertValues(source["dig"], GeneralCommandConfig);
	        this.highlow = this.convertValues(source["highlow"], GeneralCommandConfig);
	        this.hunt = this.convertValues(source["hunt"], GeneralCommandConfig);
	        this.pets = this.convertValues(source["pets"], GeneralCommandConfig);
	        this.postmemes = this.convertValues(source["postmemes"], PostMemesCommandConfig);
	        this.scratch = this.convertValues(source["scratch"], GeneralCommandConfig);
	        this.search = this.convertValues(source["search"], SearchCommandConfig);
	        this.stream = this.convertValues(source["stream"], StreamCommandConfig);
	        this.trivia = this.convertValues(source["trivia"], TriviaCommandConfig);
	        this.work = this.convertValues(source["work"], WorkCommandConfig);
	    }
	
		convertValues(a: any, classs: any, asMap: boolean = false): any {
		    if (!a) {
		        return a;
		    }
		    if (a.slice && a.map) {
		        return (a as any[]).map(elem => this.convertValues(elem, classs));
		    } else if ("object" === typeof a) {
		        if (asMap) {
		            for (const key of Object.keys(a)) {
		                a[key] = new classs(a[key]);
		            }
		            return a;
		        }
		        return new classs(a);
		    }
		    return a;
		}
	}
	export class Delays {
	    minDelay: number;
	    maxDelay: number;
	
	    static createFrom(source: any = {}) {
	        return new Delays(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.minDelay = source["minDelay"];
	        this.maxDelay = source["maxDelay"];
	    }
	}
	export class Cooldowns {
	    buttonClickDelay: Delays;
	    commandInterval: Delays;
	
	    static createFrom(source: any = {}) {
	        return new Cooldowns(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.buttonClickDelay = this.convertValues(source["buttonClickDelay"], Delays);
	        this.commandInterval = this.convertValues(source["commandInterval"], Delays);
	    }
	
		convertValues(a: any, classs: any, asMap: boolean = false): any {
		    if (!a) {
		        return a;
		    }
		    if (a.slice && a.map) {
		        return (a as any[]).map(elem => this.convertValues(elem, classs));
		    } else if ("object" === typeof a) {
		        if (asMap) {
		            for (const key of Object.keys(a)) {
		                a[key] = new classs(a[key]);
		            }
		            return a;
		        }
		        return new classs(a);
		    }
		    return a;
		}
	}
	export class GuiConfig {
	    theme: string;
	
	    static createFrom(source: any = {}) {
	        return new GuiConfig(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.theme = source["theme"];
	    }
	}
	export class Config {
	    state: boolean;
	    apiKey: string;
	    gui: GuiConfig;
	    readAlerts: boolean;
	    discordStatus: string;
	    cooldowns: Cooldowns;
	    accounts: AccountsConfig[];
	    autoBuy: AutoBuyConfig;
	    autoUse: AutoUseConfig;
	    commands: CommandsConfig;
	    adventure: AdventureConfig;
	
	    static createFrom(source: any = {}) {
	        return new Config(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.state = source["state"];
	        this.apiKey = source["apiKey"];
	        this.gui = this.convertValues(source["gui"], GuiConfig);
	        this.readAlerts = source["readAlerts"];
	        this.discordStatus = source["discordStatus"];
	        this.cooldowns = this.convertValues(source["cooldowns"], Cooldowns);
	        this.accounts = this.convertValues(source["accounts"], AccountsConfig);
	        this.autoBuy = this.convertValues(source["autoBuy"], AutoBuyConfig);
	        this.autoUse = this.convertValues(source["autoUse"], AutoUseConfig);
	        this.commands = this.convertValues(source["commands"], CommandsConfig);
	        this.adventure = this.convertValues(source["adventure"], AdventureConfig);
	    }
	
		convertValues(a: any, classs: any, asMap: boolean = false): any {
		    if (!a) {
		        return a;
		    }
		    if (a.slice && a.map) {
		        return (a as any[]).map(elem => this.convertValues(elem, classs));
		    } else if ("object" === typeof a) {
		        if (asMap) {
		            for (const key of Object.keys(a)) {
		                a[key] = new classs(a[key]);
		            }
		            return a;
		        }
		        return new classs(a);
		    }
		    return a;
		}
	}
	
	
	
	
	
	
	
	
	
	
	

}

export namespace main {
	
	export class InstanceView {
	    user?: types.User;
	    channelID: string;
	    guildID: string;
	    config: config.Config;
	    accountCfg: config.AccountsConfig;
	    lastRan: {[key: string]: time.Time};
	    pause: boolean;
	    error?: string;
	
	    static createFrom(source: any = {}) {
	        return new InstanceView(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.user = this.convertValues(source["user"], types.User);
	        this.channelID = source["channelID"];
	        this.guildID = source["guildID"];
	        this.config = this.convertValues(source["config"], config.Config);
	        this.accountCfg = this.convertValues(source["accountCfg"], config.AccountsConfig);
	        this.lastRan = this.convertValues(source["lastRan"], time.Time, true);
	        this.pause = source["pause"];
	        this.error = source["error"];
	    }
	
		convertValues(a: any, classs: any, asMap: boolean = false): any {
		    if (!a) {
		        return a;
		    }
		    if (a.slice && a.map) {
		        return (a as any[]).map(elem => this.convertValues(elem, classs));
		    } else if ("object" === typeof a) {
		        if (asMap) {
		            for (const key of Object.keys(a)) {
		                a[key] = new classs(a[key]);
		            }
		            return a;
		        }
		        return new classs(a);
		    }
		    return a;
		}
	}

}

export namespace types {
	
	export class User {
	    id: string;
	    username: string;
	    discriminator: string;
	    avatar: string;
	    bot?: boolean;
	    system?: boolean;
	    mfa_enabled?: boolean;
	    locale?: string;
	    verified?: boolean;
	    email?: string;
	    status?: string;
	
	    static createFrom(source: any = {}) {
	        return new User(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.id = source["id"];
	        this.username = source["username"];
	        this.discriminator = source["discriminator"];
	        this.avatar = source["avatar"];
	        this.bot = source["bot"];
	        this.system = source["system"];
	        this.mfa_enabled = source["mfa_enabled"];
	        this.locale = source["locale"];
	        this.verified = source["verified"];
	        this.email = source["email"];
	        this.status = source["status"];
	    }
	}

}

