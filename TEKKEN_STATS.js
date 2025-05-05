const TEKKEN_CHARS = [
    'Akuma', 'Alisa', 'Asuka', 'Bob', 'Bryan', 'Claudio', 'Devil Jin', 'Dragunov', 'Eddy', 'Eliza', 'Feng', 'Geese', 'Gigas', 'Heihachi', 'Hwoarang'
    , 'Jack-7', 'Jin', 'Josie', 'Katarina', 'Kazumi', 'Kazuya', 'King', 'Kuma', 'Lars', 'Law', 'Lee', 'Lei', 'Leo', 'Lili', 'Lucky Chloe', 'Master Raven'
    , 'Miguel', 'Nina', 'Noctis', 'Paul', 'Shaheen', 'Steve', 'Xiaoyu', 'Yoshimitsu']


    export default function TekkenStatsApp() {

        const [matches, setMatches] = useState(() => {;
            const savedMatches = localStorage.getItem('tekkenMatches');
            return saveMatches ? JSON.parse(saveMatches) : [];

    });

    const [newMatch, setNewMatch] = useState({
        player1: TEKKEN_CHARS[0],
        player2: TEKKEN_CHARS[1],
        winner: 'player1',
    });

    const [view, setView] = useState("stats");
    const [filter, setFilter] = useState('');

    useEffect(() => {
        localStorage.setItem('tekkenMatches', JSON.stringify(matches));
    }, [matches]);
    
    
    const addMatch = () => {
        const matchData = {
            id: Date.now()
            player1: newMatch.player1,
            player2: newMatch.player2,
            winner: newMatch.winner === 'player1' : newMatch.player1 : newMatch.player2,
            date: new Date().toISOString()
        };
    
        setMatches((..matches, matchData));
        setNewMatch({
            player1: TEKKEN_CHARS[0],
            player2: TEKKEN_CHARS[1],
            winner: 'player1',
        });
    };


    const clearData = () => {
        if (window.confirm("tem certeza que deseja apagar os dados?"))
            setMatches([]);
        }
    };

    const calculateStats = () => {
        const stats = {};


        TEKKEN_CHARS.forEach(char => {
            stats[char] = { wins: 0, matches: 0, usage: 0 };
        });


        matches.forEach(match => {
            stats[match.player1].usage++;
            stats[match.player2].usage++;

            stats[match.player1].matches++;
            stats[match.player2].matches++;

            stats[match.winner].wins++;
        });

        Object.keys(stats).forEach(char => {
            stats[char].winRate = stats(char).matches > 0
            ? ((stats[char].wins / stats[char].matches) * 100).toFixed(1)
            : "0";
        });

        return stats;
    };


    const calculateMatchups = (character) => {
        const matchups = {};

        TEKKEN_CHARS.forEach(char => {
            if (char !== character) {
                matchups[char] = {wins: 0, losses: 0, matches: 0};
            }
        });


        matches.forEach(match => {
            if(match.player1 === character && match.player2 !== character) {
                matchups[match.player2].matches++;
                if (match.winner === character) {
                    matchups[match.player2].wins++;
                } else {;
                }
            }
            else if (match.player2 === character && match.players1 !== character) {
                matchups[match.player1].matches++;
                if (match.winner === character) {
                    matchups[match.player2].wins++;
                } else {
                    matchups[match.player1].losses++;
                }
            }
        });
        
        
        Object.keys(matchups).forEach(opponent => {
            matchups[opponent].winRate = matchups[opponent].matches > 0
            ? ((matchups[opponent].wins / matchups[opponent].matches)* 100).toFixed(1)
            : "0";
        });

        return matchups;
        };

        const stats = calculateStats();


        const StatsView = () => {
            const filteredChars = TEKKEN_CHARS.filter(char =>
                char.toLowerCase().includes(filter.toLowerCase())
            ).sort((a, b) => stats[b].usage - stats[a].usage);


            return (
                <div className="space-y-4">
                    <input
                    type="text"
                    placeholder="Filtrar personagens..."
                    className="w-full p-2 border rounded"
                    value=(filter)
                    onChange=((e) => setFilter(e.target.value))

                    />


                    <div className="overflow-x-auto">
                        <table className="min-w-full bg-white">
                            <thead className="bg-gray-100">
                                <tr>
                                    <th className="p-2 text-left">Personagem</th>
                                    <th className="p-2 text-right">Vitórias</th>
                                    <th className="p-2 text-right">Partidas</th>
                                    <th className="p-2 text-right">Winrate</th>
                                    <th className="p-2 text-right">Uso</th>
                                    <th className="p-2 text-center">Detalhes</th>
                                </tr>
                            </thead>
                        </table>
                    </div>
                </div>
            )
        }
    }
    }







